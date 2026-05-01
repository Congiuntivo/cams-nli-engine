"""Dataset manifest loading and batch evaluation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from nli_engine.eval.comparison import ProtocolScore, ValueComparator, compare_protocols
from nli_engine.eval.metrics import SessionMetrics, compute_metrics
from nli_engine.eval.parser import parse_session


@dataclass(frozen=True)
class DatasetCase:
    """One entry in an evaluation manifest.

    Attributes:
        id: Human-readable case identifier.
        prompt: The user prompt that was (or should be) submitted to the engine.
        expected_path: Absolute path to the expected protocol JSON file.
        log_path: Absolute path to the JSONL session log for this run.
    """

    id: str
    prompt: str
    expected_path: Path
    log_path: Path


@dataclass(frozen=True)
class CaseResult:
    """Evaluation result for a single dataset case.

    Attributes:
        case_id: Identifier matching :attr:`DatasetCase.id`.
        metrics: Execution metrics derived from the session log.
        protocol_score: Key and value overlap scores between the actual and
            expected protocol. None when the session log contains no protocol
            (e.g. the workflow did not complete).
    """

    case_id: str
    metrics: SessionMetrics
    protocol_score: ProtocolScore | None


def load_manifest(path: Path) -> list[DatasetCase]:
    """Load an evaluation manifest YAML file and return its cases.

    All file paths in the manifest are resolved relative to the directory
    that contains the manifest file.

    Manifest format::

        cases:
          - id: "001_simple_diary"
            prompt: "record steps with smartphone"
            expected: cases/001_expected.json
            log: runs/001.jsonl

    Args:
        path: Path to the manifest YAML file.

    Returns:
        A list of :class:`DatasetCase` objects with absolute paths.

    Raises:
        FileNotFoundError: If *path* does not exist.
        ValueError: If the manifest is missing required fields.
    """
    base = path.parent
    with path.open() as fh:
        raw: dict[str, Any] = yaml.safe_load(fh)

    cases_raw = raw.get("cases")
    if not cases_raw:
        raise ValueError(f"Manifest at {path} has no 'cases' list.")

    cases = []
    for i, entry in enumerate(cases_raw):
        _require_fields(entry, ("id", "prompt", "expected", "log"), index=i)
        cases.append(
            DatasetCase(
                id=entry["id"],
                prompt=entry["prompt"],
                expected_path=(base / entry["expected"]).resolve(),
                log_path=(base / entry["log"]).resolve(),
            )
        )
    return cases


def evaluate_dataset(
    cases: list[DatasetCase],
    value_comparator: ValueComparator | None = None,
) -> list[CaseResult]:
    """Evaluate all cases in a dataset and return per-case results.

    Args:
        cases: List of cases as returned by :func:`load_manifest`.
        value_comparator: Optional callable for semantic value comparison.
            Passed through to :func:`~nli_engine.eval.comparison.compare_protocols`.

    Returns:
        A :class:`CaseResult` for each case, in the same order as *cases*.
    """
    return [_evaluate_case(case, value_comparator) for case in cases]


def _evaluate_case(
    case: DatasetCase,
    value_comparator: ValueComparator | None,
) -> CaseResult:
    session = parse_session(case.log_path)
    metrics = compute_metrics(session)

    actual_protocol = session.turns[-1].protocol if session.turns else None
    if actual_protocol is not None:
        expected = _load_json(case.expected_path)
        protocol_score = compare_protocols(actual_protocol, expected, value_comparator)
    else:
        protocol_score = None

    return CaseResult(
        case_id=case.id,
        metrics=metrics,
        protocol_score=protocol_score,
    )


def _load_json(path: Path) -> dict[str, Any]:
    with path.open() as fh:
        return json.load(fh)


def _require_fields(entry: dict[str, Any], fields: tuple[str, ...], index: int) -> None:
    missing = [f for f in fields if f not in entry]
    if missing:
        raise ValueError(
            f"Manifest case at index {index} is missing required fields: {missing}"
        )
