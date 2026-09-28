"""Source-specific normalization of log payloads.

The authoring-server workflows (``one_shot_llm`` and the local-model runs)
log the protocol as a flat dict. The ReAct baseline wraps it as
``{"protocol": {...}}``. HashMatch and any size counting must operate on
the flat dict, so unwrap early.

The ReAct baseline also does not emit a ``workflow_config`` event, so
:func:`synthetic_react_workflow_config` reconstructs one from the
hardcoded settings in its retrieval server / agent.
"""

from __future__ import annotations

from typing import Any

_PROTOCOL_ARRAY_FIELDS = (
    "participantRoles",
    "primaryDevices",
    "connectedDevices",
    "connections",
    "assignedDevices",
    "tasks",
    "triggers",
    "taskControls",
    "expectedParticipantData",
)


def unwrap_protocol(
    raw: dict[str, Any] | None, *, react_style: bool
) -> dict[str, Any] | None:
    """Return the flat protocol dict regardless of source-specific nesting.

    Args:
        raw: The ``turn_result.protocol`` value straight from the log, or None.
        react_style: True when the source nests as ``{"protocol": {...}}``.

    Returns:
        The flat protocol dict, or None if *raw* is None / unusable.
    """
    if raw is None:
        return None
    if react_style and isinstance(raw, dict) and set(raw.keys()) == {"protocol"}:
        inner = raw["protocol"]
        return inner if isinstance(inner, dict) else None
    return raw if isinstance(raw, dict) else None


def synthetic_react_workflow_config(model: str) -> dict[str, Any]:
    """Build a fallback ``workflow_config`` event for a ReAct-baseline log.

    The baseline's retrieval server (``retrieval_server.py``) and agent are
    hardcoded, so no ``workflow_config`` event is written to the log. The
    values below mirror those hardcoded defaults.

    Args:
        model: LLM model name, taken from the log filename.

    Returns:
        A dict shaped like a real ``workflow_config`` event (minus ``ts`` /
        ``event``) so downstream code can consume it uniformly.
    """
    return {
        "config": {
            "models": {"default": model},
            "temperatures": {},
            "parameters": {},
            "max_iterations": {},
            "retrieval": {
                "method": "dense",
                "rerank": False,
                "top_k": 5,
                "prefetch_limit": None,
                "min_score": 0.0,
                "dense_model": "ollama/mahonzhan/all-MiniLM-L6-v2",
                "sparse_model": "Qdrant/bm25",
                "multi_model": "colbert-ir/colbertv2.0",
            },
        },
        "nli_engine_git_hash": None,
    }


def protocol_sizes(protocol: dict[str, Any] | None) -> dict[str, int | None]:
    """Count array-field sizes on a (already-unwrapped) protocol.

    Args:
        protocol: Flat protocol dict returned by :func:`unwrap_protocol`.

    Returns:
        Mapping ``n_<field>`` → count. All values are None if *protocol* is None
        so the resulting row still has a stable schema.
    """
    if protocol is None:
        return {f"n_{field}": None for field in _PROTOCOL_ARRAY_FIELDS}
    return {
        f"n_{field}": len(protocol.get(field, []) or [])
        for field in _PROTOCOL_ARRAY_FIELDS
    }
