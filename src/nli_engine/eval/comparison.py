"""Protocol comparison: key overlap and value matching between actual and expected dicts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ProtocolScore:
    """Similarity scores between an actual and expected protocol dict.

    Keys are compared using their full dotted paths so that nested structure
    is taken into account. Leaf values (non-dict, non-list) are the atoms
    that are compared.

    Attributes:
        key_recall: Fraction of expected leaf keys present in the actual
            output. 1.0 means the output covers everything expected.
        key_precision: Fraction of actual leaf keys that appear in the
            expected output. 1.0 means no unexpected keys were produced.
        exact_value_match_rate: For leaf keys present in both dicts, the
            fraction whose values are identical. 0.0 when there are no
            shared keys.
        smart_value_score: Optional score from a custom
            ``value_comparator``; None when no comparator was provided.
    """

    key_recall: float
    key_precision: float
    exact_value_match_rate: float
    smart_value_score: float | None = None


ValueComparator = Callable[[str, Any, Any], float]
"""Type alias for value comparator callables.

A comparator receives ``(key_path, actual_value, expected_value)`` and
returns a similarity score in ``[0.0, 1.0]``.  Exact equality returns 1.0,
complete mismatch returns 0.0.
"""


def compare_protocols(
    actual: dict[str, Any],
    expected: dict[str, Any],
    value_comparator: ValueComparator | None = None,
) -> ProtocolScore:
    """Compare two protocol dicts and return overlap scores.

    Both dicts are flattened to ``{dotted.key.path: leaf_value}`` maps.
    List items are indexed numerically (e.g. ``tasks.0.name``).

    Args:
        actual: Protocol dict produced by the engine.
        expected: Ground-truth protocol dict.
        value_comparator: Optional callable used to score value similarity.
            When None, values are compared with strict equality (score 1.0
            for equal, 0.0 otherwise).

    Returns:
        A :class:`ProtocolScore` with recall, precision, and value-match
        metrics.
    """
    actual_flat = _flatten(actual)
    expected_flat = _flatten(expected)

    actual_keys = set(actual_flat)
    expected_keys = set(expected_flat)

    key_recall = (
        len(actual_keys & expected_keys) / len(expected_keys) if expected_keys else 1.0
    )
    key_precision = (
        len(actual_keys & expected_keys) / len(actual_keys) if actual_keys else 1.0
    )

    shared_keys = actual_keys & expected_keys
    exact_value_match_rate, smart_value_score = _score_values(
        shared_keys, actual_flat, expected_flat, value_comparator
    )

    return ProtocolScore(
        key_recall=key_recall,
        key_precision=key_precision,
        exact_value_match_rate=exact_value_match_rate,
        smart_value_score=smart_value_score,
    )


def _score_values(
    shared_keys: set[str],
    actual: dict[str, Any],
    expected: dict[str, Any],
    comparator: ValueComparator | None,
) -> tuple[float, float | None]:
    if not shared_keys:
        return 0.0, None

    exact_matches = sum(1 for k in shared_keys if actual[k] == expected[k])
    exact_rate = exact_matches / len(shared_keys)

    if comparator is None:
        return exact_rate, None

    total_smart = sum(comparator(k, actual[k], expected[k]) for k in shared_keys)
    smart_score = total_smart / len(shared_keys)
    return exact_rate, smart_score


def _flatten(
    obj: Any,
    prefix: str = "",
) -> dict[str, Any]:
    """Recursively flatten a nested dict/list into a ``{dotted.path: value}`` map.

    Args:
        obj: The object to flatten.
        prefix: Current key prefix (used in recursive calls).

    Returns:
        A flat dict mapping dotted key paths to leaf values.
    """
    result: dict[str, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            child_prefix = f"{prefix}.{key}" if prefix else key
            result.update(_flatten(value, child_prefix))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            child_prefix = f"{prefix}.{i}" if prefix else str(i)
            result.update(_flatten(value, child_prefix))
    else:
        result[prefix] = obj
    return result
