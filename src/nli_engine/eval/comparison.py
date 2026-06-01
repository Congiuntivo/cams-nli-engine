"""Protocol comparison: runs all comparison metrics and aggregates results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nli_engine.eval.hashmatch import HashMatchScore


@dataclass(frozen=True)
class ComparisonResult:
    """Aggregated comparison scores between an actual and expected protocol.

    Extensible: add new metrics as optional fields with defaults.

    Attributes:
        hashmatch: Content-addressed set F1 scores across array fields.
    """

    hashmatch: HashMatchScore


def compare_protocols(
    actual: dict[str, Any],
    expected: dict[str, Any],
) -> ComparisonResult:
    """Run all comparison metrics and return a :class:`ComparisonResult`.

    Args:
        actual: Protocol dict produced by the engine.
        expected: Ground-truth protocol dict.

    Returns:
        A :class:`ComparisonResult` populated with all metric scores.
    """
    return ComparisonResult(hashmatch=HashMatchScore.compute(actual, expected))
