from __future__ import annotations

import pytest

from nli_engine.eval.scoring.hashmatch import (
    HashMatchScore,
    _build_device_map,
    _build_task_map,
    _build_trigger_map,
    _canonical,
    _canonical_hash,
    _normalize_location_tasks,
    _normalize_task_controls,
    _rewrite_refs,
    _rewrite_trigger_device_refs,
    strip_metadata,
    to_content_addressed,
)

# ---------------------------------------------------------------------------
# strip_metadata
# ---------------------------------------------------------------------------


def test_strip_top_level_keys():
    obj = {"id": "abc", "type": "gps", "interval_seconds": 60}
    assert strip_metadata(obj) == {"type": "gps", "interval_seconds": 60}


def test_strip_nested_dict():
    obj = {"task": {"id": "t1", "name": "GPS", "type": "gps"}}
    assert strip_metadata(obj) == {"task": {"type": "gps"}}


def test_strip_inside_list():
    obj = {
        "tasks": [
            {"id": "t1", "name": "GPS", "type": "gps"},
            {"id": "t2", "name": "HR", "type": "heartrate"},
        ]
    }
    assert strip_metadata(obj) == {"tasks": [{"type": "gps"}, {"type": "heartrate"}]}


def test_preserves_non_stripped_keys():
    obj = {"type": "gps", "interval_seconds": 60, "enabled": True}
    assert strip_metadata(obj) == obj


def test_scalar_passthrough():
    assert strip_metadata("hello") == "hello"
    assert strip_metadata(42) == 42
    assert strip_metadata(None) is None


def test_empty_dict():
    assert strip_metadata({}) == {}


def test_all_keys_stripped():
    obj = {"id": "x", "name": "y", "createdOn": "2024-01-01"}
    assert strip_metadata(obj) == {}


# ---------------------------------------------------------------------------
# _canonical
# ---------------------------------------------------------------------------


def test_canonical_list_becomes_dict():
    result = _canonical([{"x": 1}, {"x": 2}])
    assert isinstance(result, dict)
    assert len(result) == 2


def test_canonical_empty_list():
    assert _canonical([]) == {}


def test_canonical_scalar_passthrough():
    assert _canonical(42) == 42
    assert _canonical("hello") == "hello"
    assert _canonical(None) is None


def test_canonical_dict_no_lists_unchanged():
    obj = {"type": "gps", "interval_seconds": 60}
    assert _canonical(obj) == obj


def test_canonical_order_invariant():
    a = _canonical([{"x": 1}, {"x": 2}])
    b = _canonical([{"x": 2}, {"x": 1}])
    assert set(a.keys()) == set(b.keys())


def test_canonical_nested_list():
    result = _canonical({"measures": [{"type": "steps"}, {"type": "hr"}]})
    assert isinstance(result["measures"], dict)
    assert len(result["measures"]) == 2


def test_canonical_nested_order_invariant():
    a = _canonical({"measures": [{"type": "steps"}, {"type": "hr"}]})
    b = _canonical({"measures": [{"type": "hr"}, {"type": "steps"}]})
    assert a == b


# ---------------------------------------------------------------------------
# _canonical_hash
# ---------------------------------------------------------------------------


def test_canonical_hash_returns_tuple():
    canonical, digest = _canonical_hash({"name": "GPS", "type": "gps"})
    assert isinstance(canonical, dict)
    assert isinstance(digest, str)
    assert len(digest) == 64


def test_canonical_hash_strips_metadata():
    canonical, _ = _canonical_hash({"id": "abc", "type": "gps"})
    assert "id" not in canonical
    assert canonical["type"] == "gps"


def test_canonical_hash_deterministic():
    _, h1 = _canonical_hash({"type": "gps", "interval_seconds": 60})
    _, h2 = _canonical_hash({"interval_seconds": 60, "type": "gps"})
    assert h1 == h2


def test_canonical_hash_nested_list_order_invariant():
    _, h1 = _canonical_hash({"measures": [{"type": "steps"}, {"type": "hr"}]})
    _, h2 = _canonical_hash({"measures": [{"type": "hr"}, {"type": "steps"}]})
    assert h1 == h2


# ---------------------------------------------------------------------------
# _build_device_map
# ---------------------------------------------------------------------------


def test_build_device_map_returns_map():
    protocol = {
        "primaryDevices": [{"roleName": "Watch", "type": "wearable"}],
        "connectedDevices": [],
    }
    device_map = _build_device_map(protocol)
    assert "Watch" in device_map
    assert len(device_map["Watch"]) == 64  # SHA-256 hex


def test_build_device_map_mutates_protocol():
    protocol = {
        "primaryDevices": [{"roleName": "Watch", "type": "wearable"}],
        "connectedDevices": [],
    }
    _build_device_map(protocol)
    assert isinstance(protocol["primaryDevices"], dict)
    assert isinstance(protocol["connectedDevices"], dict)


def test_build_device_map_missing_role_name():
    protocol = {
        "primaryDevices": [{"type": "wearable"}],
        "connectedDevices": [],
    }
    with pytest.raises(ValueError, match="roleName"):
        _build_device_map(protocol)


def test_build_device_map_same_content_different_label():
    # Two devices with identical content but different roleName → same hash
    p1 = {
        "primaryDevices": [{"roleName": "Watch", "type": "wearable"}],
        "connectedDevices": [],
    }
    p2 = {
        "primaryDevices": [{"roleName": "Smartwatch", "type": "wearable"}],
        "connectedDevices": [],
    }
    m1 = _build_device_map(p1)
    m2 = _build_device_map(p2)
    assert m1["Watch"] == m2["Smartwatch"]


# ---------------------------------------------------------------------------
# _build_task_map
# ---------------------------------------------------------------------------


def test_build_task_map_returns_map():
    protocol = {"tasks": [{"name": "GPS", "type": "gps", "interval_seconds": 60}]}
    task_map = _build_task_map(protocol)
    assert "GPS" in task_map
    assert len(task_map["GPS"]) == 64


def test_build_task_map_mutates_protocol():
    protocol = {"tasks": [{"name": "GPS", "type": "gps"}]}
    _build_task_map(protocol)
    assert isinstance(protocol["tasks"], dict)


def test_build_task_map_missing_name():
    protocol = {"tasks": [{"type": "gps"}]}
    with pytest.raises(ValueError, match="name"):
        _build_task_map(protocol)


def test_build_task_map_measures_order_invariant():
    t1 = {"name": "GPS", "measures": [{"type": "steps"}, {"type": "hr"}]}
    t2 = {"name": "GPS", "measures": [{"type": "hr"}, {"type": "steps"}]}
    m1 = _build_task_map({"tasks": [t1]})
    m2 = _build_task_map({"tasks": [t2]})
    assert m1["GPS"] == m2["GPS"]


# ---------------------------------------------------------------------------
# _build_trigger_map
# ---------------------------------------------------------------------------


def test_build_trigger_map_returns_map():
    protocol = {"triggers": {"1": {"type": "manual"}}}
    trigger_map = _build_trigger_map(protocol)
    assert "1" in trigger_map
    assert len(trigger_map["1"]) == 64


def test_build_trigger_map_mutates_protocol():
    protocol = {"triggers": {"1": {"type": "manual"}}}
    _build_trigger_map(protocol)
    assert isinstance(protocol["triggers"], dict)
    # Opaque key "1" replaced by content hash
    assert "1" not in protocol["triggers"]


def test_build_trigger_map_opaque_key_irrelevant():
    # Same content under different opaque keys → same hash
    p1 = {"triggers": {"1": {"type": "manual"}}}
    p2 = {"triggers": {"999": {"type": "manual"}}}
    m1 = _build_trigger_map(p1)
    m2 = _build_trigger_map(p2)
    assert set(m1.values()) == set(m2.values())


# ---------------------------------------------------------------------------
# _rewrite_trigger_device_refs
# ---------------------------------------------------------------------------


def test_rewrite_trigger_device_refs_rewrites_known():
    device_map = {"Watch": "hash_watch"}
    protocol = {"triggers": {"1": {"type": "manual", "sourceDeviceRoleName": "Watch"}}}
    _rewrite_trigger_device_refs(protocol, device_map, {})
    assert protocol["triggers"]["1"]["sourceDeviceRoleName"] == "hash_watch"


def test_rewrite_trigger_device_refs_unknown_left_unchanged():
    device_map = {"Watch": "hash_watch"}
    protocol = {"triggers": {"1": {"sourceDeviceRoleName": "Unknown"}}}
    _rewrite_trigger_device_refs(protocol, device_map, {})
    assert protocol["triggers"]["1"]["sourceDeviceRoleName"] == "Unknown"


def test_rewrite_trigger_device_refs_no_triggers():
    _rewrite_trigger_device_refs({}, {}, {})  # must not raise


def test_rewrite_trigger_device_refs_rewrites_task_name():
    task_map = {"My Task": "hash_task"}
    protocol = {
        "triggers": {
            "1": {"sourceDeviceRoleName": "", "taskName": "My Task"},
            "2": {"sourceDeviceRoleName": "", "taskName": "Unknown Task"},
        }
    }
    _rewrite_trigger_device_refs(protocol, {}, task_map)
    assert protocol["triggers"]["1"]["taskName"] == "hash_task"
    assert protocol["triggers"]["2"]["taskName"] == "Unknown Task"


def test_rewrite_trigger_device_refs_no_task_name_untouched():
    protocol = {"triggers": {"1": {"sourceDeviceRoleName": ""}}}
    _rewrite_trigger_device_refs(protocol, {}, {})
    assert "taskName" not in protocol["triggers"]["1"]


# ---------------------------------------------------------------------------
# _rewrite_refs
# ---------------------------------------------------------------------------


def test_rewrite_refs_connections():
    device_map = {"Watch": "hash_watch", "Phone": "hash_phone"}
    protocol = {"connections": [{"roleName": "Watch", "connectedToRoleName": "Phone"}]}
    result = _rewrite_refs(protocol, device_map, {}, {})
    conn = result["connections"][0]
    assert conn["roleName"] == "hash_watch"
    assert conn["connectedToRoleName"] == "hash_phone"


def test_rewrite_refs_task_controls():
    device_map = {"Watch": "hash_watch"}
    task_map = {"GPS": "hash_gps"}
    trigger_map = {"1": "hash_trigger"}
    protocol = {
        "taskControls": [
            {"destinationDeviceRoleName": "Watch", "taskName": "GPS", "triggerId": "1"}
        ]
    }
    result = _rewrite_refs(protocol, device_map, task_map, trigger_map)
    ctrl = result["taskControls"][0]
    assert ctrl["destinationDeviceRoleName"] == "hash_watch"
    assert ctrl["taskName"] == "hash_gps"
    assert ctrl["triggerId"] == "hash_trigger"


def test_rewrite_refs_unknown_labels_unchanged():
    protocol = {"connections": [{"roleName": "Ghost", "connectedToRoleName": "Ghost"}]}
    result = _rewrite_refs(protocol, {}, {}, {})
    conn = result["connections"][0]
    assert conn["roleName"] == "Ghost"


# ---------------------------------------------------------------------------
# to_content_addressed
# ---------------------------------------------------------------------------

_MINIMAL_PROTOCOL: dict = {
    "primaryDevices": [{"roleName": "Watch", "type": "wearable"}],
    "connectedDevices": [],
    "tasks": [{"name": "GPS", "type": "gps"}, {"name": "HR", "type": "heartrate"}],
    "triggers": {"1": {"type": "manual", "sourceDeviceRoleName": "Watch"}},
    "connections": [{"roleName": "Watch", "connectedToRoleName": "Watch"}],
    "taskControls": [
        {"destinationDeviceRoleName": "Watch", "taskName": "GPS", "triggerId": "1"}
    ],
}


def _minimal() -> dict:
    import copy

    return copy.deepcopy(_MINIMAL_PROTOCOL)


def test_to_content_addressed_all_arrays_become_dicts():
    result = to_content_addressed(_minimal())
    for field in ("primaryDevices", "tasks", "triggers", "connections", "taskControls"):
        assert isinstance(result[field], dict), f"{field} should be a dict"


def test_to_content_addressed_task_order_invariant():
    import copy

    p1 = _minimal()
    p2 = copy.deepcopy(_MINIMAL_PROTOCOL)
    p2["tasks"] = list(reversed(p2["tasks"]))
    r1 = to_content_addressed(p1)
    r2 = to_content_addressed(p2)
    assert set(r1["tasks"].keys()) == set(r2["tasks"].keys())


# ---------------------------------------------------------------------------
# _normalize_task_controls
# ---------------------------------------------------------------------------

# Synthetic hash strings
_HTASK_A = "task_a" * 5  # task A hash
_HTASK_B = "task_b" * 5  # task B hash
_HTASK_C = "task_c" * 5  # task C hash
_HTASK_D = "task_d" * 5  # task D hash

_HTR = "trigger" * 5  # trigger hash
_HTR2 = "trigger2" * 5  # second trigger hash
_HDEV = "device" * 5  # device hash

_TASK_A = {"__type": "BackgroundTask", "measures": {"m1": {"type": "gps"}}}
_TASK_B = {"__type": "BackgroundTask", "measures": {"m2": {"type": "hr"}}}
_TASK_C = {"__type": "OtherTask", "measures": {"m3": {"type": "fr"}}}
_TASK_D = {
    "__type": "BackgroundTask",
    "otherField": 42,
    "measures": {"m2": {"type": "hr"}},
}


def _proto_with_four_tasks() -> dict:
    """Canonical-state protocol with four distinct tasks."""
    return {
        "tasks": {
            _HTASK_A: _TASK_A,
            _HTASK_B: _TASK_B,
            _HTASK_C: _TASK_C,
            _HTASK_D: _TASK_D,
        },
        "triggers": {},
        "taskControls": [
            {
                "triggerId": _HTR,
                "taskName": _HTASK_A,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            {
                "triggerId": _HTR,
                "taskName": _HTASK_B,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            {
                "triggerId": _HTR,
                "taskName": _HTASK_C,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            {
                "triggerId": _HTR,
                "taskName": _HDEV,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
        ],
    }


def test_normalize_merge_A_and_B():
    result = _normalize_task_controls(_proto_with_four_tasks())

    assert len(result["taskControls"]) == 3  # merged AB + C + D

    assert _HTASK_A not in result["tasks"]
    assert _HTASK_B not in result["tasks"]

    assert _HTASK_C in result["tasks"]
    assert _HTASK_D in result["tasks"]

    assert len(result["tasks"]) == 3  # merged_AB + C + D


def _proto_with_two_tcs(task_a=None, task_b=None, trigger_ref=None):
    """Canonical-state protocol with two taskControls sharing the same key."""
    return {
        "tasks": {
            _HTASK_A: task_a or _TASK_A,
            _HTASK_B: task_b or _TASK_B,
        },
        "triggers": {},
        "taskControls": [
            {
                "triggerId": _HTR,
                "taskName": _HTASK_A,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            {
                "triggerId": _HTR,
                "taskName": _HTASK_B,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
        ],
    }


def test_normalize_basic_merge():
    result = _normalize_task_controls(_proto_with_two_tcs())

    assert len(result["taskControls"]) == 1
    assert len(result["tasks"]) == 1

    merged_task = next(iter(result["tasks"].values()))
    assert merged_task["__type"] == "BackgroundTask"
    assert "m1" in merged_task["measures"]
    assert "m2" in merged_task["measures"]

    merged_hash = result["taskControls"][0]["taskName"]
    assert merged_hash in result["tasks"]


def test_normalize_trigger_locked_blocks_merge():
    protocol = _proto_with_two_tcs()
    # Lock task A via a trigger taskName reference
    protocol["triggers"] = {"th": {"sourceDeviceRoleName": _HDEV, "taskName": _HTASK_A}}

    result = _normalize_task_controls(protocol)

    assert len(result["taskControls"]) == 2
    assert _HTASK_A in result["tasks"]
    assert _HTASK_B in result["tasks"]


def test_normalize_locked_task_excluded_others_still_merge():
    # 3 tasks in the same group: A (locked), B and C (unlocked).
    # B and C must merge; A must keep its own taskControl.
    task_c = {"__type": "BackgroundTask", "measures": {"m3": {"type": "steps"}}}
    protocol = {
        "tasks": {_HTASK_A: _TASK_A, _HTASK_B: _TASK_B, _HTASK_C: task_c},
        "triggers": {"th": {"sourceDeviceRoleName": _HDEV, "taskName": _HTASK_A}},
        "taskControls": [
            {
                "triggerId": _HTR,
                "taskName": _HTASK_A,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            {
                "triggerId": _HTR,
                "taskName": _HTASK_B,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            {
                "triggerId": _HTR,
                "taskName": _HTASK_C,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
        ],
    }

    result = _normalize_task_controls(protocol)

    assert len(result["taskControls"]) == 2  # A's TC + merged BC TC
    assert _HTASK_A in result["tasks"]
    assert _HTASK_B not in result["tasks"]
    assert _HTASK_C not in result["tasks"]
    assert len(result["tasks"]) == 2  # A + merged_BC

    merged_task = next(v for h, v in result["tasks"].items() if h != _HTASK_A)
    assert "m2" in merged_task["measures"]
    assert "m3" in merged_task["measures"]


def test_normalize_mixed_types_partial_merge():
    # BackgroundTask A + B share a kind → merge.
    # AppTask C is a different kind → stays as its own TC.
    task_c_app = {"__type": "AppTask", "measures": {"m3": {"type": "image"}}}
    protocol = {
        "tasks": {_HTASK_A: _TASK_A, _HTASK_B: _TASK_B, _HTASK_C: task_c_app},
        "triggers": {},
        "taskControls": [
            {
                "triggerId": _HTR,
                "taskName": _HTASK_A,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            {
                "triggerId": _HTR,
                "taskName": _HTASK_B,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            {
                "triggerId": _HTR,
                "taskName": _HTASK_C,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
        ],
    }

    result = _normalize_task_controls(protocol)

    assert len(result["taskControls"]) == 2  # merged_AB + C
    assert _HTASK_A not in result["tasks"]
    assert _HTASK_B not in result["tasks"]
    assert _HTASK_C in result["tasks"]

    merged_task = next(v for h, v in result["tasks"].items() if h != _HTASK_C)
    assert merged_task["__type"] == "BackgroundTask"
    assert "m1" in merged_task["measures"]
    assert "m2" in merged_task["measures"]


def test_normalize_different_type_blocks_merge():
    task_b_app = {"__type": "AppTask", "measures": {"m2": {"type": "hr"}}}
    protocol = _proto_with_two_tcs(task_b=task_b_app)

    result = _normalize_task_controls(protocol)

    assert len(result["taskControls"]) == 2
    assert _HTASK_A in result["tasks"]
    assert _HTASK_B in result["tasks"]


def test_normalize_different_non_measures_field_blocks_merge():
    task_b_diff = {
        "__type": "BackgroundTask",
        "duration": 999,
        "measures": {"m2": {"type": "hr"}},
    }
    protocol = _proto_with_two_tcs(task_b=task_b_diff)

    result = _normalize_task_controls(protocol)

    assert len(result["taskControls"]) == 2


def test_normalize_task_in_multiple_groups():
    # taskA appears in group1 (trigger _HT / device _HD) and group2 (trigger _HT2 / device _HD)
    task_c = {"__type": "BackgroundTask", "measures": {"m3": {"type": "steps"}}}
    protocol = {
        "tasks": {_HTASK_A: _TASK_A, _HTASK_B: _TASK_B, _HTASK_C: task_c},
        "triggers": {},
        "taskControls": [
            # group1: A + B → mergedAB
            {
                "triggerId": _HTR,
                "taskName": _HTASK_A,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            {
                "triggerId": _HTR,
                "taskName": _HTASK_B,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            # group2: A + C → mergedAC
            {
                "triggerId": _HTR2,
                "taskName": _HTASK_A,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            {
                "triggerId": _HTR2,
                "taskName": _HTASK_C,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
        ],
    }

    result = _normalize_task_controls(protocol)

    assert len(result["taskControls"]) == 2
    # Two merged tasks; original A, B, C all removed
    assert _HTASK_A not in result["tasks"]
    assert _HTASK_B not in result["tasks"]
    assert _HTASK_C not in result["tasks"]
    assert len(result["tasks"]) == 2


def test_hashmatch_score_split_equals_merged():
    split = {
        "primaryDevices": [{"roleName": "Phone", "__type": "Smartphone"}],
        "connectedDevices": [],
        "tasks": [
            {
                "name": "Task A",
                "__type": "BackgroundTask",
                "measures": [{"type": "gps"}],
            },
            {
                "name": "Task B",
                "__type": "BackgroundTask",
                "measures": [{"type": "hr"}],
            },
        ],
        "triggers": {
            "1": {"__type": "ImmediateTrigger", "sourceDeviceRoleName": "Phone"}
        },
        "connections": [],
        "taskControls": [
            {
                "destinationDeviceRoleName": "Phone",
                "taskName": "Task A",
                "triggerId": "1",
                "control": "Start",
            },
            {
                "destinationDeviceRoleName": "Phone",
                "taskName": "Task B",
                "triggerId": "1",
                "control": "Start",
            },
        ],
    }
    merged = {
        "primaryDevices": [{"roleName": "Phone", "__type": "Smartphone"}],
        "connectedDevices": [],
        "tasks": [
            {
                "name": "Task AB",
                "__type": "BackgroundTask",
                "measures": [{"type": "gps"}, {"type": "hr"}],
            },
        ],
        "triggers": {
            "1": {"__type": "ImmediateTrigger", "sourceDeviceRoleName": "Phone"}
        },
        "connections": [],
        "taskControls": [
            {
                "destinationDeviceRoleName": "Phone",
                "taskName": "Task AB",
                "triggerId": "1",
                "control": "Start",
            },
        ],
    }

    score = HashMatchScore.compute(split, merged)

    assert score.per_field["tasks"].f1 == 1.0
    assert score.per_field["taskControls"].f1 == 1.0
    assert score.f1 == 1.0


def test_to_content_addressed_device_label_invariant():
    # Renaming a device (same content, different roleName) must not change
    # the device hash or any cross-reference hashes.
    import copy

    p1 = _minimal()

    p2 = copy.deepcopy(_MINIMAL_PROTOCOL)
    for d in p2["primaryDevices"]:
        d["roleName"] = "Smartwatch"
    for conn in p2["connections"]:
        conn["roleName"] = "Smartwatch"
        conn["connectedToRoleName"] = "Smartwatch"
    for ctrl in p2["taskControls"]:
        ctrl["destinationDeviceRoleName"] = "Smartwatch"
    for t in p2["triggers"].values():
        t["sourceDeviceRoleName"] = "Smartwatch"

    r1 = to_content_addressed(p1)
    r2 = to_content_addressed(p2)

    assert set(r1["primaryDevices"].keys()) == set(r2["primaryDevices"].keys())
    assert set(r1["connections"].keys()) == set(r2["connections"].keys())
    assert set(r1["taskControls"].keys()) == set(r2["taskControls"].keys())


_HEALTH_MEASURE_A = "WEIGHT"
_HEALTH_MEASURE_B = "SLEEP_LIGHT"
_HEALTH_MEASURE_C = "BODY_MASS_INDEX"
_HEALTH_MEASURE_D = "SLEEP_ASLEEP"

_HASH_HMA = "health_task_a" * 2
_HASH_HMB = "health_task_b" * 2
_HASH_HMC = "health_task_c" * 2
_HASH_HMD = "health_task_d" * 2

_HEALTH_TASK_A = {
    "__type": "BackgroundTask",
    "measures": {
        "m1": {
            "__type": "dk.cachet.carp.common.application.tasks.Measure.DataStream",
            "type": "dk.cachet.carp.health",
            "overrideSamplingConfiguration": {
                "__type": "dk.cachet.carp.common.application.sampling.HealthSamplingConfiguration",
                "past": 2592000000000,
                "future": 86400000000,
                "healthDataTypes": {
                    _HASH_HMA: _HEALTH_MEASURE_A,
                    _HASH_HMB: _HEALTH_MEASURE_B,
                },
            },
        }
    },
}

_HEALTH_TASK_B = {
    "__type": "BackgroundTask",
    "measures": {
        "m1": {
            "__type": "dk.cachet.carp.common.application.tasks.Measure.DataStream",
            "type": "dk.cachet.carp.health",
            "overrideSamplingConfiguration": {
                "__type": "dk.cachet.carp.common.application.sampling.HealthSamplingConfiguration",
                "past": 2592000000000,
                "future": 86400000000,
                "healthDataTypes": {
                    _HASH_HMC: _HEALTH_MEASURE_C,
                    _HASH_HMD: _HEALTH_MEASURE_D,
                },
            },
        }
    },
}

_EXPECTED_MERGED_HEALTH_MEASURE = {
    "__type": "dk.cachet.carp.common.application.tasks.Measure.DataStream",
    "type": "dk.cachet.carp.health",
    "overrideSamplingConfiguration": {
        "__type": "dk.cachet.carp.common.application.sampling.HealthSamplingConfiguration",
        "past": 2592000000000,
        "future": 86400000000,
        "healthDataTypes": {
            _HASH_HMA: _HEALTH_MEASURE_A,
            _HASH_HMB: _HEALTH_MEASURE_B,
            _HASH_HMC: _HEALTH_MEASURE_C,
            _HASH_HMD: _HEALTH_MEASURE_D,
        },
    },
}


def _proto_with_health_tasks() -> dict:
    return {
        "tasks": {_HTASK_A: _HEALTH_TASK_A, _HTASK_B: _HEALTH_TASK_B},
        "triggers": {},
        "taskControls": [
            {
                "triggerId": _HTR,
                "taskName": _HTASK_A,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
            {
                "triggerId": _HTR,
                "taskName": _HTASK_B,
                "destinationDeviceRoleName": _HDEV,
                "control": "Start",
            },
        ],
    }


def test_normalize_health_tasks_merge():
    result = _normalize_task_controls(_proto_with_health_tasks())

    assert len(result["taskControls"]) == 1
    assert len(result["tasks"]) == 1

    merged_task = next(iter(result["tasks"].values()))
    merged_measure = next(iter(merged_task["measures"].values()))

    assert merged_measure == _EXPECTED_MERGED_HEALTH_MEASURE, (
        "Health measures should be merged correctly"
    )


# ---------------------------------------------------------------------------
# _normalize_location_tasks
# ---------------------------------------------------------------------------

_HPHONE = "phone_dev" * 4  # synthetic Smartphone hash
_HLOC_SVC = "loc_svc_" * 4  # synthetic LocationService hash
_HLOC_TASK = "loc_task" * 4  # synthetic task hash for location-sensing task
_HOTHER_TASK = "other_ta" * 4  # synthetic task hash for non-location task
_HTR_LOC = "trig_loc" * 4  # synthetic trigger hash


def _proto_for_location_normalization(
    *,
    destination: str = _HLOC_SVC,
    task_hash: str = _HLOC_TASK,
    include_location_service: bool = True,
) -> dict:
    """Build a canonical-state protocol fragment for location normalization tests."""
    connected: dict = {}
    if include_location_service:
        connected[_HLOC_SVC] = {
            "__type": "dk.carp.cams.devices.LocationService",
            "defaultSamplingConfiguration": {},
        }
    return {
        "primaryDevices": {
            _HPHONE: {
                "__type": "dk.carp.cams.devices.Smartphone",
                "isPrimaryDevice": True,
                "defaultSamplingConfiguration": {},
            }
        },
        "connectedDevices": connected,
        "tasks": {
            _HLOC_TASK: {
                "__type": "dk.cachet.carp.common.application.tasks.BackgroundTask",
                "measures": {
                    "m_loc": {
                        "__type": "dk.cachet.carp.common.application.tasks.Measure.DataStream",
                        "type": "dk.cachet.carp.location",
                    }
                },
            },
            _HOTHER_TASK: {
                "__type": "dk.cachet.carp.common.application.tasks.BackgroundTask",
                "measures": {
                    "m_hr": {
                        "__type": "dk.cachet.carp.common.application.tasks.Measure.DataStream",
                        "type": "dk.cachet.carp.heartrate",
                    }
                },
            },
        },
        "triggers": {},
        "taskControls": [
            {
                "triggerId": _HTR_LOC,
                "taskName": task_hash,
                "destinationDeviceRoleName": destination,
                "control": "Start",
            }
        ],
    }


def test_normalize_location_task_on_location_service_redirected_to_phone():
    proto = _proto_for_location_normalization(
        destination=_HLOC_SVC, task_hash=_HLOC_TASK
    )
    result = _normalize_location_tasks(proto)
    assert result["taskControls"][0]["destinationDeviceRoleName"] == _HPHONE


def test_normalize_location_task_already_on_phone_unchanged():
    proto = _proto_for_location_normalization(destination=_HPHONE, task_hash=_HLOC_TASK)
    result = _normalize_location_tasks(proto)
    assert result["taskControls"][0]["destinationDeviceRoleName"] == _HPHONE


def test_normalize_non_location_task_on_location_service_unchanged():
    proto = _proto_for_location_normalization(
        destination=_HLOC_SVC, task_hash=_HOTHER_TASK
    )
    result = _normalize_location_tasks(proto)
    assert result["taskControls"][0]["destinationDeviceRoleName"] == _HLOC_SVC


def test_normalize_location_no_location_service_noop():
    proto = _proto_for_location_normalization(
        destination=_HLOC_SVC, task_hash=_HLOC_TASK, include_location_service=False
    )
    result = _normalize_location_tasks(proto)
    # No LocationService in connectedDevices → protocol returned unchanged
    assert result["taskControls"][0]["destinationDeviceRoleName"] == _HLOC_SVC
