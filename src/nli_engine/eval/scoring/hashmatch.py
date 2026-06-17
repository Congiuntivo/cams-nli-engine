"""HashMatch: content-addressed set F1 for structured protocol comparison.

Evaluation design follows the component-wise F1 approach introduced for
text-to-SQL in:

    Yu et al. (2018). Spider: A Large-Scale Human-Labeled Dataset for Complex
    and Cross-Domain Semantic Parsing and Text-to-SQL Task. EMNLP 2018.
    https://doi.org/10.18653/v1/d18-1425

Each top-level protocol category (devices, tasks, triggers, …) is scored
independently as a set-comparison F1, then macro-averaged across categories.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any

_COLLECTION_FIELDS: frozenset[str] = frozenset(
    {
        "primaryDevices",
        "connectedDevices",
        "tasks",
        "triggers",
        "taskControls",
        "connections",
    }
)

_NAMED_FIELDS: frozenset[str] = _COLLECTION_FIELDS | {"applicationData"}

STRIPPED_KEYS: frozenset[str] = frozenset(
    {
        "createdOn",
        "description",
        "id",
        "name",
        "ownerId",
        "roleName",
    }
)


@dataclass(frozen=True)
class FieldScore:
    """HashMatch scores for a single array field.

    Attributes:
        precision: TP / (TP + FP) — fraction of generated elements that were correct.
        recall: TP / (TP + FN) — fraction of expected elements that were generated.
        f1: Harmonic mean of precision and recall.
        tp: Elements present in both actual and expected.
        fp: Elements in actual but not expected (hallucinated).
        fn: Elements in expected but not actual (missed).
    """

    precision: float
    recall: float
    f1: float
    tp: int
    fp: int
    fn: int

    @classmethod
    def from_sets(cls, actual: set[str], expected: set[str]) -> "FieldScore":
        """Compute a :class:`FieldScore` from two sets of content hashes.

        Both-empty is treated as a perfect match (P=R=F1=1).

        Args:
            actual: Content hashes from the generated protocol field.
            expected: Content hashes from the ground-truth protocol field.

        Returns:
            A :class:`FieldScore` with TP/FP/FN and derived P/R/F1.
        """
        tp = len(actual & expected)
        fp = len(actual - expected)
        fn = len(expected - actual)

        if actual or expected:
            p = tp / len(actual) if actual else 0.0
            r = tp / len(expected) if expected else 0.0
            f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        else:
            p = r = f1 = 1.0

        return cls(precision=p, recall=r, f1=f1, tp=tp, fp=fp, fn=fn)


@dataclass(frozen=True)
class HashMatchScore:
    """Aggregated HashMatch scores across all array fields in a protocol.

    Attributes:
        f1: Macro-averaged F1 across all array fields.
        precision: Macro-averaged precision.
        recall: Macro-averaged recall.
        per_field: Per-field breakdown keyed by field name.
    """

    f1: float
    precision: float
    recall: float
    per_field: dict[str, FieldScore]

    @classmethod
    def compute(
        cls, actual: dict[str, Any], expected: dict[str, Any]
    ) -> "HashMatchScore":
        """Compute HashMatch F1 between two protocol dicts.

        Steps:
            1. ``to_content_addressed`` on both inputs (handles stripping internally).
            2. Split each into per-category hash sets via :func:`_split_categories`.
            3. For every category present in either dict, compute :meth:`FieldScore.from_sets`.
            4. Macro-average F1 / precision / recall across all categories.

        Args:
            actual: Protocol dict produced by the engine.
            expected: Ground-truth protocol dict.

        Returns:
            A :class:`HashMatchScore` with per-field and macro-averaged scores.
        """
        ca_actual = to_content_addressed(copy.deepcopy(actual))
        ca_expected = to_content_addressed(copy.deepcopy(expected))

        actual_cats = _split_categories(ca_actual)
        expected_cats = _split_categories(ca_expected)

        all_cats = actual_cats.keys() | expected_cats.keys()
        per_field: dict[str, FieldScore] = {
            cat: FieldScore.from_sets(
                actual_cats.get(cat, set()), expected_cats.get(cat, set())
            )
            for cat in all_cats
        }

        n = len(per_field)
        macro_p = sum(s.precision for s in per_field.values()) / n
        macro_r = sum(s.recall for s in per_field.values()) / n
        macro_f1 = sum(s.f1 for s in per_field.values()) / n

        return cls(f1=macro_f1, precision=macro_p, recall=macro_r, per_field=per_field)


def strip_metadata(obj: Any) -> Any:
    """Recursively remove non-functional metadata keys from a protocol dict.

    Args:
        obj: A dict, list, or scalar value.

    Returns:
        A copy of *obj* with all keys in :data:`STRIPPED_KEYS` removed at
        every level of nesting.
    """
    if isinstance(obj, dict):
        return {k: strip_metadata(v) for k, v in obj.items() if k not in STRIPPED_KEYS}
    if isinstance(obj, list):
        return [strip_metadata(item) for item in obj]
    return obj


def to_content_addressed(protocol: dict[str, Any]) -> dict[str, Any]:
    """Convert a raw protocol dict into a fully content-addressed form.

    Takes the raw (unstripped) protocol so that natural keys (``roleName``,
    task ``name``, trigger IDs) are still available to build cross-reference
    maps before they are stripped away.  All stripping happens internally
    when computing element hashes.

    Steps:
        1. Build device, task, and trigger maps via :func:`_build_device_map`,
           :func:`_build_task_map`, and :func:`_build_trigger_map`.  Each map
           builder reads natural keys before stripping, then mutates *protocol*
           in place to replace the corresponding array with a content-addressed
           dict ``{sha256_hex: canonical_element}``.
           :func:`_rewrite_trigger_device_refs` is called between the task and
           trigger map builds so that trigger hashes are stable with respect to
           device labels.
        2. Rewrite remaining cross-references (``connections``,
           ``taskControls``) from human-chosen labels to stable content hashes
           via :func:`_rewrite_refs`.
        3. Apply :func:`_canonical` to convert any remaining lists (e.g.
           ``connections``, ``taskControls``) to content-addressed dicts at
           every nesting depth.

    Args:
        protocol: Raw protocol dict as returned by the server.  Mutated in
            place by the map-building steps.

    Returns:
        A fully content-addressed dict where every array field at every depth
        is replaced by ``{sha256_hex: canonical_element}`` and all
        cross-references are stable content hashes.
    """
    device_map = _build_device_map(protocol)
    task_map = _build_task_map(protocol)
    _rewrite_trigger_device_refs(protocol, device_map, task_map)

    trigger_map = _build_trigger_map(protocol)
    protocol = _rewrite_refs(protocol, device_map, task_map, trigger_map)
    protocol = _normalize_location_tasks(protocol)
    protocol = _normalize_task_controls(protocol)
    protocol = strip_metadata(protocol)
    return _canonical(protocol)


def _split_categories(ca_protocol: dict[str, Any]) -> dict[str, set[str]]:
    """Split a content-addressed protocol into per-category hash sets.

    Collection fields (``primaryDevices``, ``tasks``, etc.) yield the set of
    their dict keys, which are already content hashes.  Atomic named fields
    (e.g. ``dataEndpoint``) are hashed as a single unit.  All remaining
    top-level keys are bucketed into ``"other"`` by hashing each
    ``[key, value]`` pair.

    Args:
        ca_protocol: Content-addressed protocol from :func:`to_content_addressed`.

    Returns:
        Dict mapping category name to a set of content hashes.
    """
    result: dict[str, set[str]] = {}
    other: set[str] = set()

    for key, value in ca_protocol.items():
        if key in _NAMED_FIELDS:
            result[key] = set(value.keys()) if isinstance(value, dict) else set()
        else:
            other.add(_hash_element([key, value]))

    if other:
        result["other"] = other

    return result


def _hash_element(element: Any) -> str:
    """Return a hex SHA-256 digest of *element* serialised as canonical JSON.

    Args:
        element: Any JSON-serialisable value.

    Returns:
        A 64-character hex string.
    """
    payload = json.dumps(element, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def _canonical(obj: Any) -> Any:
    """Recursively convert all lists to content-addressed dicts.

    Called on already-stripped content before hashing, so that nested arrays
    are order-invariant at every depth.

    Args:
        obj: A stripped dict, list, or scalar.

    Returns:
        A copy of *obj* where every list is replaced by
        ``{sha256_hex: canonical_element}``.
    """
    if isinstance(obj, dict):
        return {k: _canonical(v) for k, v in obj.items()}
    if isinstance(obj, list):
        items = [_canonical(item) for item in obj]
        return {_hash_element(item): item for item in items}
    return obj


def _canonical_hash(obj: Any) -> tuple[Any, str]:
    """Strip metadata, canonicalize, and hash *obj*.

    Args:
        obj: Raw (unstripped) element.

    Returns:
        ``(canonical, hex_digest)`` where *canonical* is the stripped,
        content-addressed form and *hex_digest* is its SHA-256 hash.
    """
    c = _canonical(strip_metadata(obj))
    return c, _hash_element(c)


def _merge_task_measures(task_bodies: list[dict[str, Any]]) -> dict[str, Any]:
    """Union measures across tasks, merging health measures by kind.

    Non-health measures are merged by plain dict union (measure key → value).
    Health measures (``type == "dk.cachet.carp.health"``) are grouped by their
    structural kind — the measure serialised with ``healthDataTypes`` removed from
    ``overrideSamplingConfiguration`` — and their ``healthDataTypes`` dicts are
    unioned within each kind group, producing one merged measure per group.

    This handles both the case where two health measures have different hash keys
    (real canonicalized data) and the case where they share the same synthetic key
    (unit tests), in either case producing one measure per kind with the full union
    of health data types.

    Args:
        task_bodies: Canonical task dicts (post-``_build_task_map``) whose measures
            are to be merged.

    Returns:
        A ``{measure_key: measure}`` dict suitable for use as the ``measures``
        field of the merged task.
    """
    non_health: dict[str, Any] = {}
    health_groups: dict[str, dict[str, Any]] = {}

    for body in task_bodies:
        for measure_key, measure in body.get("measures", {}).items():
            if measure.get("type") != "dk.cachet.carp.health":
                non_health[measure_key] = measure
                continue

            sampling_cfg = measure.get("overrideSamplingConfiguration", {})
            kind_cfg = {k: v for k, v in sampling_cfg.items() if k != "healthDataTypes"}
            kind_measure = {
                k: v for k, v in measure.items() if k != "overrideSamplingConfiguration"
            }
            kind_measure["overrideSamplingConfiguration"] = kind_cfg
            kind_key = json.dumps(kind_measure, sort_keys=True)

            if kind_key not in health_groups:
                health_groups[kind_key] = {
                    "template": measure,
                    "healthDataTypes": dict(sampling_cfg.get("healthDataTypes", {})),
                }
            else:
                health_groups[kind_key]["healthDataTypes"].update(
                    sampling_cfg.get("healthDataTypes", {})
                )

    result = dict(non_health)
    for group in health_groups.values():
        template = group["template"]
        merged_sampling = {
            **template["overrideSamplingConfiguration"],
            "healthDataTypes": group["healthDataTypes"],
        }
        merged_measure = {**template, "overrideSamplingConfiguration": merged_sampling}
        result[_hash_element(merged_measure)] = merged_measure

    return result


def _normalize_location_tasks(protocol: dict[str, Any]) -> dict[str, Any]:
    """Redirect location-sensing tasks from LocationService to Smartphone.

    A task is a location-sensing task if any of its measures has
    ``type == "dk.cachet.carp.location"``.  Such tasks, when assigned to a
    ``LocationService`` device via ``taskControls.destinationDeviceRoleName``,
    are semantically equivalent to the same task assigned to the primary
    ``Smartphone`` device.  This function rewrites
    ``destinationDeviceRoleName`` in every matching taskControl from the
    LocationService hash to the Smartphone hash so that subsequent task
    merging can treat them uniformly.

    Called after :func:`_rewrite_refs` (all cross-references are stable
    content hashes) and before :func:`_normalize_task_controls`.

    Args:
        protocol: Protocol dict after :func:`_rewrite_refs`.

    Returns:
        A shallow copy of *protocol* with taskControls rewritten.
    """
    location_service_hashes = {
        h
        for h, dev in protocol.get("connectedDevices", {}).items()
        if dev.get("__type") == "dk.carp.cams.devices.LocationService"
    }
    if not location_service_hashes:
        return protocol

    phone_hash = next(
        (
            h
            for h, dev in protocol.get("primaryDevices", {}).items()
            if dev.get("__type") == "dk.carp.cams.devices.Smartphone"
        ),
        None,
    )
    if phone_hash is None:
        return protocol

    location_task_hashes = {
        h
        for h, task in protocol.get("tasks", {}).items()
        if any(
            m.get("type") == "dk.cachet.carp.location"
            for m in task.get("measures", {}).values()
        )
    }
    if not location_task_hashes:
        return protocol

    result = dict(protocol)
    result["taskControls"] = [
        {**tc, "destinationDeviceRoleName": phone_hash}
        if (
            tc.get("destinationDeviceRoleName") in location_service_hashes
            and tc.get("taskName") in location_task_hashes
        )
        else tc
        for tc in protocol.get("taskControls", [])
    ]
    return result


def _normalize_task_controls(protocol: dict[str, Any]) -> dict[str, Any]:
    """Normalize split/merged task equivalence before final canonicalization.

    Two CARP protocols that express the same study behaviour — one using
    separate tasks per taskControl (split form) and one using a single task
    with merged measures (merged form) — must score identically.  This
    function detects groups of taskControls sharing the same
    ``(triggerId, destinationDeviceRoleName, control)`` key and, where all
    tasks in the group are eligible, replaces them with a single taskControl
    pointing to a new merged task whose ``measures`` is the union.

    Called after :func:`_rewrite_refs` (all cross-references are stable
    content hashes) and before :func:`strip_metadata` /
    :func:`_canonical` (``taskControls`` is still a list).

    Within each group, tasks referenced by a trigger ``taskName`` field
    (trigger-locked) are passed through as individual taskControls and excluded
    from merging.  The remaining unlocked tasks are sub-grouped by *kind* —
    the JSON-serialised non-``measures`` body (which includes ``__type`` and
    all other structural fields).  Tasks with the same kind key are structurally
    compatible and have their measures merged; tasks in different kind sub-groups
    are each left as their own taskControl.  Original task hashes are removed
    from ``protocol["tasks"]`` only after all groups are processed, to handle
    tasks shared across groups.

    Args:
        protocol: Protocol dict after :func:`_rewrite_refs`.

    Returns:
        A shallow copy of *protocol* with normalized ``taskControls`` (list)
        and ``tasks`` (dict).
    """
    task_controls: list[dict[str, Any]] = protocol.get("taskControls", [])
    tasks: dict[str, Any] = protocol.get("tasks", {})

    locked_tasks: set[str] = set()
    for trigger in protocol.get("triggers", {}).values():
        if "taskName" in trigger:
            locked_tasks.add(trigger["taskName"])

    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for tc in task_controls:
        key = (
            tc.get("triggerId", ""),
            tc.get("destinationDeviceRoleName", ""),
            tc.get("control", ""),
        )
        groups.setdefault(key, []).append(tc)

    new_tasks: dict[str, Any] = dict(tasks)
    new_task_controls: list[dict[str, Any]] = []
    to_remove: set[str] = set()

    for group in groups.values():
        # Locked tasks must stay as individual taskControls regardless of group size.
        # The remaining unlocked tasks are then considered for merging independently.
        locked_tcs = [tc for tc in group if tc["taskName"] in locked_tasks]
        unlocked_tcs = [tc for tc in group if tc["taskName"] not in locked_tasks]

        new_task_controls.extend(locked_tcs)

        kind_groups: dict[str, list[dict[str, Any]]] = {}
        for tc in unlocked_tcs:
            body = tasks.get(tc["taskName"])
            if body is None:
                new_task_controls.append(tc)
                print(
                    f"Warning: taskControl references unknown task '{tc['taskName']}'; skipping merge for this taskControl"
                )
                continue
            kind_key = json.dumps(
                {k: v for k, v in body.items() if k != "measures"},
                sort_keys=True,
            )
            kind_groups.setdefault(kind_key, []).append(tc)

        for kind_tcs in kind_groups.values():
            if len(kind_tcs) < 2:
                new_task_controls.extend(kind_tcs)
                continue

            task_hashes = [tc["taskName"] for tc in kind_tcs]
            task_bodies = [tasks[h] for h in task_hashes]

            merged_measures = _merge_task_measures(task_bodies)

            merged_task = {**task_bodies[0], "measures": merged_measures}
            merged_hash = _hash_element(merged_task)

            new_tasks[merged_hash] = merged_task
            to_remove.update(task_hashes)
            new_task_controls.append({**kind_tcs[0], "taskName": merged_hash})

    still_referenced = {tc["taskName"] for tc in new_task_controls}
    for h in to_remove:
        if h not in still_referenced:
            new_tasks.pop(h, None)

    result = dict(protocol)
    result["tasks"] = new_tasks
    result["taskControls"] = new_task_controls
    return result


def _build_device_map(protocol: dict[str, Any]) -> dict[str, str]:
    """Build a ``roleName → content_hash`` map for all devices.

    Processes each device via :func:`_canonical_hash` (strip metadata,
    canonicalize nested arrays, hash), and mutates *protocol* in place by
    replacing ``primaryDevices`` and ``connectedDevices`` with
    content-addressed dicts ``{content_hash: canonical_device}``.

    Args:
        protocol: Raw (unstripped) protocol dict.

    Returns:
        Dict mapping each device ``roleName`` to its content hash.

    Raises:
        ValueError: If any device is missing a ``roleName`` field.
    """
    result: dict[str, str] = {}

    new_fields: dict[str, dict[str, Any]] = {}
    for field in ("primaryDevices", "connectedDevices"):
        new_fields[field] = {}
        for device_config in protocol.get(field, []):
            role_name = device_config.get("roleName")
            if role_name is None:
                raise ValueError(
                    f"Device in field '{field}' is missing 'roleName': {device_config}"
                )

            device_config, content_hash = _canonical_hash(device_config)

            result[role_name] = content_hash
            new_fields[field][content_hash] = device_config

    protocol.update(new_fields)
    return result


def _build_task_map(protocol: dict[str, Any]) -> dict[str, str]:
    """Build a ``taskName → content_hash`` map for all tasks.

    Processes each task via :func:`_canonical_hash` (strip metadata,
    canonicalize nested arrays, hash), and mutates *protocol* in place by
    replacing ``tasks`` with a content-addressed dict
    ``{content_hash: canonical_task}``.

    Args:
        protocol: Raw (unstripped) protocol dict.

    Returns:
        Dict mapping each task ``name`` to its content hash.

    Raises:
        ValueError: If any task is missing a ``name`` field.
    """
    result: dict[str, str] = {}
    new_tasks: dict[str, Any] = {}

    for task in protocol.get("tasks", []):
        task_name = task.get("name")
        if task_name is None:
            raise ValueError(f"Task is missing 'name': {task}")

        stripped, content_hash = _canonical_hash(task)

        result[task_name] = content_hash
        new_tasks[content_hash] = stripped

    protocol["tasks"] = new_tasks
    return result


def _rewrite_trigger_device_refs(
    protocol: dict[str, Any],
    device_map: dict[str, str],
    task_map: dict[str, str],
) -> None:
    """Rewrite cross-reference fields in every trigger to stable content hashes.

    Rewrites ``sourceDeviceRoleName`` via *device_map* and, for trigger types
    that reference a task by name (``NoUserTaskTrigger``, ``UserTaskTrigger``),
    rewrites ``taskName`` via *task_map*.  Must be called after
    :func:`_build_device_map` and :func:`_build_task_map` and before
    :func:`_build_trigger_map` so that trigger hashes are stable regardless of
    the labels chosen by the LLM.  Mutates ``protocol["triggers"]`` in place.

    Args:
        protocol: Protocol dict (mutated in place).
        device_map: ``roleName → content_hash`` map from :func:`_build_device_map`.
        task_map: ``taskName → content_hash`` map from :func:`_build_task_map`.
    """
    triggers = protocol.get("triggers")
    if not isinstance(triggers, dict):
        return
    for trigger_value in triggers.values():
        source = trigger_value.get("sourceDeviceRoleName", "")
        trigger_value["sourceDeviceRoleName"] = device_map.get(source, source)
        if "taskName" in trigger_value:
            raw = trigger_value["taskName"]
            trigger_value["taskName"] = task_map.get(raw, raw)


def _build_trigger_map(protocol: dict[str, Any]) -> dict[str, str]:
    """Build a ``triggerId → content_hash`` map for all triggers.

    ``triggers`` is a pseudo-array dict with opaque numeric string keys.
    Processes each trigger via :func:`_canonical_hash` (strip metadata,
    canonicalize nested arrays, hash); the opaque key is discarded.  Mutates
    *protocol* in place by replacing ``triggers`` with a content-addressed dict
    ``{content_hash: canonical_trigger}``.

    Args:
        protocol: Protocol dict (mutated in place).

    Returns:
        Dict mapping each trigger id (as a string) to its content hash.
    """
    result: dict[str, str] = {}
    new_triggers: dict[str, Any] = {}
    for trigger_id, trigger_value in protocol.get("triggers", {}).items():
        content, content_hash = _canonical_hash(trigger_value)
        result[str(trigger_id)] = content_hash
        new_triggers[content_hash] = content
    protocol["triggers"] = new_triggers
    return result


def _rewrite_refs(
    protocol: dict[str, Any],
    device_map: dict[str, str],
    task_map: dict[str, str],
    trigger_map: dict[str, str],
) -> dict[str, Any]:
    """Replace natural-key cross-references with their stable content hashes.

    Rewrites these fields in-place on a shallow copy of *protocol*:

    - ``connections[*].roleName`` and ``connectedToRoleName`` → device hash
    - ``taskControls[*].destinationDeviceRoleName`` → device hash
    - ``taskControls[*].taskName`` → task hash
    - ``taskControls[*].triggerId`` → trigger hash

    ``triggers[*].sourceDeviceRoleName`` is handled earlier by
    :func:`_rewrite_trigger_device_refs` so that trigger hashes are stable
    before :func:`_build_trigger_map` runs.

    Unknown labels (not present in the maps) are left unchanged.

    Args:
        protocol: Protocol dict after :func:`_build_*` maps have been built.
        device_map: ``roleName → hash`` for all devices.
        task_map: ``taskName → hash`` for all tasks.
        trigger_map: ``triggerId → hash`` for all triggers.

    Returns:
        A shallow copy of *protocol* with cross-references rewritten.
    """
    result = dict(protocol)

    if "connections" in result:
        result["connections"] = [
            {
                **conn,
                "roleName": device_map.get(
                    conn.get("roleName", ""), conn.get("roleName", "")
                ),
                "connectedToRoleName": device_map.get(
                    conn.get("connectedToRoleName", ""),
                    conn.get("connectedToRoleName", ""),
                ),
            }
            for conn in result["connections"]
        ]

    if "taskControls" in result:
        result["taskControls"] = [
            {
                **ctrl,
                "destinationDeviceRoleName": device_map.get(
                    ctrl.get("destinationDeviceRoleName", ""),
                    ctrl.get("destinationDeviceRoleName", ""),
                ),
                "taskName": task_map.get(
                    ctrl.get("taskName", ""), ctrl.get("taskName", "")
                ),
                "triggerId": trigger_map.get(
                    str(ctrl.get("triggerId", "")), str(ctrl.get("triggerId", ""))
                ),
            }
            for ctrl in result["taskControls"]
        ]

    return result
