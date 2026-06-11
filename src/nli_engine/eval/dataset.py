"""Dataset manifest loading and batch evaluation."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from nli_engine.eval.comparison import ComparisonResult, compare_protocols
from nli_engine.eval.metrics import SessionMetrics, compute_metrics
from nli_engine.eval.parser import parse_session

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class DatasetCase:
    """One entry in an evaluation manifest.

    Attributes:
        id: Human-readable case identifier.
        prompts: Map of prompt_key → prompt_text. Multiple prompts may target
            the same gold-standard protocol (e.g. varying richness levels).
        expected_path: Absolute path to the expected protocol JSON file.
    """

    id: str
    prompts: dict[str, str]
    expected_path: Path


@dataclass(frozen=True)
class ResolvedCase:
    """A dataset case bound to a specific log file, ready for evaluation.

    Attributes:
        case_id: Identifier matching :attr:`DatasetCase.id`.
        prompt_key: Key within :attr:`DatasetCase.prompts` that matched the log.
        prompt: The prompt text that was used.
        expected_path: Absolute path to the expected protocol JSON file.
        log_path: Absolute path to the JSONL session log.
    """

    case_id: str
    prompt_key: str
    prompt: str
    expected_path: Path
    log_path: Path


@dataclass(frozen=True)
class CaseResult:
    """Evaluation result for a single dataset case.

    Attributes:
        case_id: Identifier matching :attr:`DatasetCase.id`.
        prompt_key: Which prompt variant was evaluated.
        metrics: Execution metrics derived from the session log.
        comparison: Comparison scores between the actual and expected protocol.
            None when the session log contains no protocol (e.g. the workflow
            did not complete).
    """

    case_id: str
    prompt_key: str
    metrics: SessionMetrics
    comparison: ComparisonResult | None


def load_manifest(path: Path) -> list[DatasetCase]:
    """Load an evaluation manifest YAML file and return its cases.

    All file paths in the manifest are resolved relative to the directory
    that contains the manifest file.

    Manifest format::

        cases:
          - id: "001_simple_diary"
            expected: cases/001_expected.json
            prompts:
              v1: "record steps with smartphone"
              detailed: "record steps and location every hour..."

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
        _require_fields(entry, ("id", "prompts", "expected"), index=i)
        prompts = entry["prompts"]
        if not isinstance(prompts, dict) or not prompts:
            raise ValueError(
                f"Manifest case at index {i}: 'prompts' must be a non-empty mapping."
            )
        cases.append(
            DatasetCase(
                id=entry["id"],
                prompts=prompts,
                expected_path=(base / entry["expected"]).resolve(),
            )
        )
    return cases


def evaluate_dataset(cases: list[ResolvedCase]) -> list[CaseResult]:
    """Evaluate all resolved cases and return per-case results.

    Args:
        cases: List of resolved cases as returned by :func:`resolve_last_from`
            or :func:`resolve_from_log`.

    Returns:
        A :class:`CaseResult` for each case, in the same order as *cases*.
    """
    return [_evaluate_case(case) for case in cases]


def resolve_last_from(cases: list[DatasetCase], logs_dir: Path) -> list[ResolvedCase]:
    """For each (case, prompt_key) pair, find the most recent matching log in *logs_dir*.

    Scans all ``*.jsonl`` files under *logs_dir*, reads the first ``user_turn``
    event from each to extract the prompt text, and builds a map from prompt text
    to the most recently modified matching file (by ``mtime``).  Each
    ``(case, prompt_key)`` whose prompt text has a match produces a
    :class:`ResolvedCase`; unmatched pairs are skipped with a warning.

    Args:
        cases: Cases as returned by :func:`load_manifest`.
        logs_dir: Directory to scan for ``.jsonl`` log files.

    Returns:
        A list of :class:`ResolvedCase` with one entry per matched
        ``(case_id, prompt_key)`` pair.

    Raises:
        FileNotFoundError: If *logs_dir* does not exist.
    """
    if not logs_dir.exists():
        raise FileNotFoundError(f"Logs directory not found: {logs_dir}")

    best: dict[str, tuple[float, Path]] = {}
    for log_file in logs_dir.glob("*.jsonl"):
        prompt = _extract_prompt(log_file)
        if prompt is None:
            continue
        mtime = log_file.stat().st_mtime
        if prompt not in best or mtime > best[prompt][0]:
            best[prompt] = (mtime, log_file)

    resolved: list[ResolvedCase] = []
    for case in cases:
        for key, text in case.prompts.items():
            if text in best:
                resolved.append(
                    ResolvedCase(
                        case_id=case.id,
                        prompt_key=key,
                        prompt=text,
                        expected_path=case.expected_path,
                        log_path=best[text][1].resolve(),
                    )
                )
            else:
                log.warning(
                    "No log found for case %r prompt_key %r — skipping.", case.id, key
                )
    return resolved


def resolve_from_log(cases: list[DatasetCase], log_path: Path) -> ResolvedCase:
    """Find the manifest case and prompt key that match the given log file.

    Extracts the first ``user_turn`` text from *log_path* and searches all
    ``(case, prompt_key)`` pairs in *cases* for an exact match.

    Args:
        cases: Cases as returned by :func:`load_manifest`.
        log_path: Path to the ``.jsonl`` log file to match.

    Returns:
        A :class:`ResolvedCase` for the matched case and prompt key.

    Raises:
        ValueError: If *log_path* contains no ``user_turn`` event, or if no
            manifest case matches the prompt text.
    """
    prompt = _extract_prompt(log_path)
    if prompt is None:
        raise ValueError(f"No user_turn found in {log_path}")
    for case in cases:
        for key, text in case.prompts.items():
            if text == prompt:
                return ResolvedCase(
                    case_id=case.id,
                    prompt_key=key,
                    prompt=text,
                    expected_path=case.expected_path,
                    log_path=log_path.resolve(),
                )
    raise ValueError(f"No manifest case matches the user_turn in {log_path!r}")


def _evaluate_case(case: ResolvedCase) -> CaseResult:
    session = parse_session(case.log_path)
    metrics = compute_metrics(session)

    actual_protocol = session.turns[-1].protocol if session.turns else None
    if actual_protocol is not None:
        expected = _load_json(case.expected_path)
        comparison = compare_protocols(actual_protocol, expected)
    else:
        comparison = None

    return CaseResult(
        case_id=case.case_id,
        prompt_key=case.prompt_key,
        metrics=metrics,
        comparison=comparison,
    )


def _extract_prompt(path: Path) -> str | None:
    """Return the first user_turn text from a JSONL log, or None if absent."""
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("event") == "user_turn":
                return event.get("text")
    return None


def _load_json(path: Path) -> dict[str, Any]:
    with path.open() as fh:
        return json.load(fh)


def _require_fields(entry: dict[str, Any], fields: tuple[str, ...], index: int) -> None:
    missing = [f for f in fields if f not in entry]
    if missing:
        raise ValueError(
            f"Manifest case at index {index} is missing required fields: {missing}"
        )
