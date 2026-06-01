# HashMatch

HashMatch is the comparison metric used when evaluating generated protocols against
a gold-standard expected protocol. It replaced the flat key-overlap approach
(`compare_protocols`) entirely. The old metric flattened the protocol into dotted
key paths (`tasks.0.name`, `tasks.1.name`, …), which fails for arrays because
array elements have no stable positional identity — an element at index 0 in the
expected output may be at index 2 in the generated output, or present but
reordered, with no change in functional meaning.

---

## Why key overlap is not enough

- The generated output may contain the correct elements in a different order.
- Leaf paths like `tasks.0.name` only match if both outputs agree on position,
  not just content.
- The protocol's `triggers` field is a JSON object used as a pseudo-array
  (keys are opaque IDs, values are trigger objects), so it cannot be indexed
  positionally at all.

The result is false negatives: two protocols that are functionally identical
can score poorly because their arrays happen to be in different order.

---

## Core idea

HashMatch converts every array (and every pseudo-array) in both protocols into
a **content-addressed dict**: each element becomes an entry whose key is a
deterministic hash of that element's content. Comparison then becomes a
standard set operation — elements are matched by what they _are_, not where
they _sit_.

Two elements are considered the same if and only if their hashed content is
identical after non-functional metadata has been stripped.

---

## Scoring approach

The scoring design follows the **component-wise F1** approach introduced for
text-to-SQL evaluation in:

> Yu et al. (2018). _Spider: A Large-Scale Human-Labeled Dataset for Complex
> and Cross-Domain Semantic Parsing and Text-to-SQL Task._ EMNLP 2018.
> <https://doi.org/10.18653/v1/d18-1425>

Rather than computing a single global set F1, HashMatch decomposes the protocol
into **named categories** and scores each independently:

| Category           | How it is scored                                                  |
| ------------------ | ----------------------------------------------------------------- |
| `primaryDevices`   | Set F1 over content hashes of device elements                     |
| `connectedDevices` | Set F1 over content hashes of device elements                     |
| `tasks`            | Set F1 over content hashes of task elements                       |
| `triggers`         | Set F1 over content hashes of trigger elements                    |
| `taskControls`     | Set F1 over content hashes of task-control elements               |
| `connections`      | Set F1 over content hashes of connection elements                 |
| `dataEndpoint`     | Present / absent match (hashed as a single atomic unit)           |
| `other`            | Set F1 over `[key, value]` pairs for all remaining top-level keys |

The final `HashMatchScore` is the **macro-average** of F1, precision, and recall
across all categories present in either protocol. Every category is weighted
equally regardless of how many elements it contains, so a missing `dataEndpoint`
penalises the score just as much as a completely wrong `tasks` array.

---

## Algorithm

### Step 1 — Build content-addressed maps for devices, tasks, and triggers

For each of `primaryDevices`, `connectedDevices`, `tasks`, and `triggers`, the
corresponding `_build_*` function:

1. Reads each element's **natural key** (the human-chosen label: `roleName` for
   devices, `name` for tasks, the opaque numeric key for triggers) before
   stripping, because these labels appear as cross-references elsewhere in the
   protocol and must be resolved before they are erased.
2. Processes the element through `_canonical_hash`: strip non-functional
   metadata, recursively convert all nested lists to content-addressed dicts
   (so that e.g. a task's `measures` list is also order-invariant), then hash
   the result.
3. Mutates the protocol in place, replacing the original array with a
   content-addressed dict `{sha256_hex: canonical_element}`.
4. Returns a `natural_key → content_hash` map for use in cross-reference
   rewriting.

#### Non-functional keys stripped before hashing

| Key           | Category             |
| ------------- | -------------------- |
| `id`          | Database / server ID |
| `ownerId`     | Database / server ID |
| `name`        | Human-readable label |
| `roleName`    | Human-readable label |
| `description` | Human-readable label |
| `createdOn`   | Timestamp            |

> **Why strip names and role names?** The LLM is free to assign any label it
> likes (e.g. `"GPS Task"` vs `"GPS Tracking"`). Two tasks that configure the
> same sensor at the same rate are functionally identical regardless of their
> name. Stripping labels before hashing means label choice never affects the
> score.

#### Nested arrays are canonicalized before hashing

A task may contain a list of measures, a device may contain a list of
configurations, and so on. `_canonical` is applied recursively before hashing
so that every list at every depth is converted to a content-addressed dict.
This makes the parent element's hash order-invariant at all levels of nesting.

### Step 2 — Rewrite cross-references to stable content hashes

Several fields in the protocol reference other elements by their natural key:

| Field                                       | Cross-reference    |
| ------------------------------------------- | ------------------ |
| `triggers[*].sourceDeviceRoleName`          | device `roleName`  |
| `connections[*].roleName`                   | device `roleName`  |
| `connections[*].connectedToRoleName`        | device `roleName`  |
| `taskControls[*].destinationDeviceRoleName` | device `roleName`  |
| `taskControls[*].taskName`                  | task `name`        |
| `taskControls[*].triggerId`                 | trigger opaque key |

After step 1, the natural-key → content_hash maps are known. Every cross-reference
field is rewritten to its stable content hash so that the referencing element's
own hash is independent of the human-chosen label.

> **Trigger timing:** `triggers[*].sourceDeviceRoleName` must be rewritten
> _before_ triggers are hashed, so that trigger hashes do not depend on device
> labels. `_rewrite_trigger_device_refs` is therefore called between the device
> map build and the trigger map build.

### Step 3 — Canonicalize remaining arrays

After steps 1 and 2, `primaryDevices`, `connectedDevices`, `tasks`, and
`triggers` are already content-addressed dicts. The remaining array fields
(`connections`, `taskControls`, and any future additions) are still plain lists.
`_canonical` is applied to the full protocol to convert them:

- Recurses into every dict at every depth.
- For every list encountered, replaces it with `{sha256(canonical_element): canonical_element}`.

Because all cross-references in `connections` and `taskControls` have already
been rewritten to content hashes in step 2, the resulting hashes are stable
regardless of what labels the LLM chose.

### Step 4 — Convert arrays to content-addressed dicts (illustration)

**Before (raw protocol fragment):**

```json
"tasks": [
  { "id": "t1", "name": "GPS", "type": "gps", "interval_seconds": 60 },
  { "id": "t2", "name": "HR",  "type": "heartrate", "interval_seconds": 3600 }
]
```

**After stripping and hashing:**

```json
"tasks": {
  "a3f8c1...": { "type": "gps", "interval_seconds": 60 },
  "9d72b4...": { "type": "heartrate", "interval_seconds": 3600 }
}
```

Both the generated and expected protocols go through steps 1–3. The result is
two structurally comparable dicts where every array at every depth has been
replaced by a set of content-addressed entries.

### Step 5 — Compute set F1 per category, then macro-average

`_split_categories` partitions the content-addressed protocol into per-category
hash sets (see the [Scoring approach](#scoring-approach) table above). For each
category present in either protocol, collect:

- **True positives (TP):** hash keys present in both generated and expected
- **False positives (FP):** hash keys in generated but not expected (hallucinated elements)
- **False negatives (FN):** hash keys in expected but not generated (missed elements)

From these, derive:

| Score         | Formula             | Meaning                                           |
| ------------- | ------------------- | ------------------------------------------------- |
| **Precision** | TP / (TP + FP)      | What fraction of generated elements were correct  |
| **Recall**    | TP / (TP + FN)      | What fraction of expected elements were generated |
| **F1**        | 2 · P · R / (P + R) | Harmonic mean; 1.0 = perfect match                |

When both actual and expected sets for a category are empty the category scores
P = R = F1 = 1.0 (both protocols correctly agree that it is absent).

The overall score is the **macro-average** of F1, precision, and recall across
all categories. The result is a `HashMatchScore` with full per-category
breakdowns accessible in `HashMatchScore.per_field`.

---

## Handling the triggers pseudo-array

The protocol's `triggers` field is a JSON object where each key is an opaque
numeric string (`"1"`, `"2"`, …). This is structurally a dict but semantically
an array — the keys carry no meaning.

HashMatch treats it identically to a real array: the existing opaque keys are
ignored, each value is processed through `_canonical_hash`, and the resulting
content-addressed dict is compared as a set.

---

## Integration

`HashMatchScore.compute(actual, expected)` is the entry point. It is called by
`compare_protocols` in `comparison.py`, which wraps the result in a
`ComparisonResult`:

```python
@dataclass(frozen=True)
class ComparisonResult:
    hashmatch: HashMatchScore
```

`compare_protocols(actual, expected)` returns a `ComparisonResult`. Additional
metrics can be added as new typed fields without breaking existing callers.

---

## What HashMatch does not cover

- **Scalar field correctness** — numeric parameters (`interval_seconds`,
  `threshold`, …) must still match exactly for two elements to hash the same.
  Partial credit for "close" numeric values is out of scope.
- **Label / name quality** — names are stripped before hashing, so HashMatch
  cannot tell you whether the LLM chose a good label. A separate metric or
  manual review is needed for that.
- **Element-level diffs** — when a hash key is missing (FN or FP), HashMatch
  records the miss but does not explain which field inside the element was
  wrong. Use the raw diffs alongside the score for debugging.

---

## Example walkthrough

**Expected protocol:**

```json
{
  "tasks": [
    { "id": "t1", "name": "GPS", "type": "gps", "interval_seconds": 60 },
    { "id": "t2", "name": "HR", "type": "heartrate", "interval_seconds": 3600 }
  ]
}
```

**Generated protocol:**

```json
{
  "tasks": [
    {
      "id": "x9",
      "name": "Heart Rate Monitor",
      "type": "heartrate",
      "interval_seconds": 3600
    },
    { "id": "x7", "name": "Location", "type": "gps", "interval_seconds": 60 },
    { "id": "x3", "name": "Steps", "type": "pedometer", "interval_seconds": 30 }
  ]
}
```

**After stripping `id` and `name`:**

Expected elements: `{type: gps, interval: 60}`, `{type: heartrate, interval: 3600}`
Generated elements: `{type: heartrate, interval: 3600}`, `{type: gps, interval: 60}`, `{type: pedometer, interval: 30}`

**After hashing (simplified):**

| Hash           | In expected | In generated |
| -------------- | ----------- | ------------ |
| `hash_gps_60`  | ✓           | ✓            |
| `hash_hr_3600` | ✓           | ✓            |
| `hash_pedo_30` | —           | ✓            |

TP = 2, FP = 1, FN = 0 → Precision = 0.67, Recall = 1.0, **F1 = 0.80**

The metric correctly identifies that both expected tasks were generated (perfect
recall) and that one extra task was hallucinated (imperfect precision), despite
the arrays being in different order and the names being completely different.
