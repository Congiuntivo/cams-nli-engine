from __future__ import annotations

import pytest

from nli_engine.eval.scoring.hashmatch import (
    _build_device_map,
    _build_task_map,
    _build_trigger_map,
    _canonical,
    _canonical_hash,
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
    _rewrite_trigger_device_refs(protocol, device_map)
    assert protocol["triggers"]["1"]["sourceDeviceRoleName"] == "hash_watch"


def test_rewrite_trigger_device_refs_unknown_left_unchanged():
    device_map = {"Watch": "hash_watch"}
    protocol = {"triggers": {"1": {"sourceDeviceRoleName": "Unknown"}}}
    _rewrite_trigger_device_refs(protocol, device_map)
    assert protocol["triggers"]["1"]["sourceDeviceRoleName"] == "Unknown"


def test_rewrite_trigger_device_refs_no_triggers():
    _rewrite_trigger_device_refs({}, {})  # must not raise


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
