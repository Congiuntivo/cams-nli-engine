# Prompt design — richness levels

How the dataset prompts are constructed for the 3x3 (case × richness) grid.

## Goal

For each of the 3 cases (001 easy, 002 medium, 003 hard), provide 3 prompt variants at three richness levels — **poor**, **medium**, **rich** — that all map to the **same** `expected.json` for that case.

The case-complexity axis and the prompt-richness axis are independent. Eval observes the system's behavior across both.

## Fixed-protocol constraint

The expected protocol per case does not change across richness levels. The poor prompt must therefore still elicit the full protocol — it cannot omit components. What varies is how the components are _described_, not which ones are present.

This makes "poor" the most constrained variant to write: it has to cover everything in the protocol while sounding casual, short, and non-technical.

## Richness levels

| level      | structure                           | vocabulary                                                                         | length                         | inference allowed                                                   |
| ---------- | ----------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------- |
| **poor**   | short casual sentences, no markdown | lay terms only ("keep checking", "always show", "after they finish")               | shortest, but still exhaustive | trivial structural mapping (see below)                              |
| **medium** | continuous prose, no markdown       | semi-technical ("every 30 minutes", "in the background", "until the user is done") | mid                            | small naming choices (e.g., "every 30 minutes" → `PeriodicTrigger`) |
| **rich**   | markdown headings + nested bullets  | CARP-aware (names trigger types, measure types, device classes)                    | longest                        | none — fully explicit                                               |

## Trivial inference rule (poor level)

The poor prompt may describe a _behavior_ and rely on the system to map it to a CARP primitive. It may not omit specific values or specific subsets.

**Allowed — structural mapping from behavior**

- "the user can do it whenever they want, always available" → `NoUserTaskTrigger`
- "after the user records the diary, then ask them to take a photo" → `UserTaskTrigger(done)`
- "an hour after the study starts" → `ElapsedTimeTrigger(1h)`
- "every morning around 9" → `RecurrentScheduledTrigger(daily, 09:00)`
- "track this passively in the background" → `ImmediateTrigger` + `BackgroundTask`

**Not allowed — specific values or subsets must be enumerated, even in lay terms**

- "common cardio metrics" → must enumerate: "heart rate, resting heart rate, heart rate variability (RMSSD and SDNN), blood pressure (systolic and diastolic), blood oxygen"
- "every now and then" → must give a frequency
- "some health data" → must list each type
- "wearables for the heart" → must name Polar / Movesense

## Richness vector (descriptive measurement)

Reported per prompt, no composite score — same pattern as the complexity vector for cases. Lets the thesis claim "we placed the prompts at three distinct richness levels" be inspectable rather than asserted.

| prompt | token count | # markdown elements (headings, bullets) | # CARP-technical terms | type-token ratio |
| ------ | ----------- | --------------------------------------- | ---------------------- | ---------------- |

Computation is a small offline script over the prompt strings.

## Storage convention

- **Poor and medium prompts** are short enough to live inline as single-line double-quoted strings in `manifest.yaml`.
- **Rich prompts** are stored as separate markdown files under `dataset/prompts/<case-prefix>_<richness>.md` (e.g. `003_rich.md`). The `<case-prefix>` is the leading underscore-delimited segment of the case `id`. `dataset/inline_rich_prompts.py` reads each file and inlines its contents under the matching `prompts.<richness>` key in `manifest.yaml` as a YAML literal block scalar (`|`), preserving newlines exactly. Rerun the script whenever a rich `.md` file changes.

The `.md` files are the source of truth; the inlined manifest is a generated artifact.

> Note on YAML form: rich prompts use the `|` block scalar rather than single-line `"..."` with escaped `\n`. The escaped form gets reformatted to multi-line by some YAML linters, after which YAML's folding rule silently collapses single newlines into spaces and corrupts the markdown.

## Grid status

| case         | poor | medium | rich      |
| ------------ | ---- | ------ | --------- |
| 001 (easy)   | v1   | v2     | v3 (file) |
| 002 (medium) | v3   | v1, v2 | v4 (file) |
| 003 (hard)   | v1   | v2     | v3 (file) |

`vN` keys reference entries in `manifest.yaml`. Numbering is chronological (existing keys preserved); richness is annotated as a YAML comment on each line. Rich prompts marked "(file)" live as `prompts/<case>_<v>_rich.md` and are inlined into the manifest by the (TBD) build script.

Existing prompts classified by inspection:

- 001 v1 ("Record steps with the smartphone…") — **poor** (short, casual, lay vocabulary, leaves trigger-type inference).
- 002 v1 / v2 — **medium** (continuous prose, semi-technical, fully specified; small wording variant between v1 and v2).
