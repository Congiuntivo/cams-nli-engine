"""Handler for the ``nli-eval aggregate`` subcommand."""

from __future__ import annotations

import csv
import json
import re
import sys
from argparse import Namespace
from dataclasses import asdict
from pathlib import Path
from typing import Any

from rich.console import Console

from nli_engine.eval.io.dataset import DatasetCase, load_manifest
from nli_engine.eval.io.parser import parse_session
from nli_engine.eval.scoring.hashmatch import HashMatchScore
from nli_engine.eval.scoring.metrics import SessionMetrics, compute_metrics

_FILENAME_RE = re.compile(
    r"^(?P<model>.+?)_(?P<case_id>\d{3}_[a-z_]+?)"
    r"_(?P<prompt>poor|medium|rich)_run(?P<run>\d+)$"
)

_CSV_COLUMNS = [
    "source",
    "model",
    "case_id",
    "prompt_key",
    "run",
    "workflow_complete",
    "n_turns",
    "n_llm_calls",
    "n_tool_rounds",
    "n_tool_calls",
    "n_failed_tool_calls",
    "tool_failure_rate",
    "total_input_tokens",
    "total_output_tokens",
    "total_latency_ms",
    "hm_f1",
    "hm_precision",
    "hm_recall",
]


def cmd_aggregate(args: Namespace) -> None:
    """Aggregate execution metrics + HashMatch across a batch of session logs.

    Walks ``<base>/*/results/*.jsonl`` (default base: ``study/runs``), computes
    :class:`~nli_engine.eval.scoring.metrics.SessionMetrics` and
    :class:`~nli_engine.eval.scoring.hashmatch.HashMatchScore` per log, and
    writes one row per log to CSV (flat, macro-only HashMatch) and/or JSON
    (with per-field HashMatch nested).

    Filenames must match ``<model>_<caseId>_<prompt>_run<NN>.jsonl`` where
    ``caseId`` is an id present in the manifest and ``prompt`` is one of
    ``poor|medium|rich``. The ``source`` column is derived from the parent
    directory name (e.g. ``models`` / ``local_models``).

    Args:
        args: Parsed arguments. Expected attributes: ``manifest`` (Path),
            ``base`` (Path), ``csv`` (Path | None), ``json`` (Path | None).
    """
    console = Console()

    if args.csv is None and args.json is None:
        console.print("[red]Error:[/red] Provide at least one of --csv or --json.")
        sys.exit(1)

    try:
        cases = load_manifest(args.manifest)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    cases_by_id: dict[str, DatasetCase] = {c.id: c for c in cases}
    expected_cache: dict[str, dict[str, Any]] = {}

    log_files = sorted(args.base.glob("*/results/*.jsonl"))
    if not log_files:
        console.print(
            f"[yellow]No log files found under {args.base}/*/results/[/yellow]"
        )
        sys.exit(1)

    console.print(f"Found {len(log_files)} log file(s).")

    rows: list[dict[str, Any]] = []
    for log_path in log_files:
        row = _process_log(log_path, cases_by_id, expected_cache, console)
        if row is not None:
            rows.append(row)

    console.print(f"Processed {len(rows)} log(s).")

    if args.csv:
        _write_csv(rows, args.csv)
        console.print(f"[dim]CSV written to {args.csv}[/dim]")
    if args.json:
        _write_json(rows, args.json)
        console.print(f"[dim]JSON written to {args.json}[/dim]")


def _process_log(
    log_path: Path,
    cases_by_id: dict[str, DatasetCase],
    expected_cache: dict[str, dict[str, Any]],
    console: Console,
) -> dict[str, Any] | None:
    """Parse one log, compute metrics + HashMatch, return a row dict."""
    match = _FILENAME_RE.match(log_path.stem)
    if match is None:
        console.print(
            f"[yellow]Skip[/yellow] {log_path.name}: filename does not match pattern"
        )
        return None

    case_id = match["case_id"]
    case = cases_by_id.get(case_id)
    if case is None:
        console.print(
            f"[yellow]Skip[/yellow] {log_path.name}: case {case_id!r} not in manifest"
        )
        return None

    try:
        session = parse_session(log_path)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[yellow]Skip[/yellow] {log_path.name}: {exc}")
        return None

    metrics = compute_metrics(session)

    hashmatch: HashMatchScore | None = None
    actual_protocol = session.turns[-1].protocol if session.turns else None
    if actual_protocol is not None:
        if case_id not in expected_cache:
            with case.expected_path.open() as fh:
                expected_cache[case_id] = json.load(fh)
        try:
            hashmatch = HashMatchScore.compute(actual_protocol, expected_cache[case_id])
        except (ValueError, KeyError) as exc:
            console.print(
                f"[yellow]HashMatch failed[/yellow] for {log_path.name}: {exc}"
            )

    return _build_row(
        source=log_path.parent.parent.name,
        model=match["model"],
        case_id=case_id,
        prompt_key=match["prompt"],
        run=int(match["run"]),
        metrics=metrics,
        hashmatch=hashmatch,
    )


def _build_row(
    source: str,
    model: str,
    case_id: str,
    prompt_key: str,
    run: int,
    metrics: SessionMetrics,
    hashmatch: HashMatchScore | None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "source": source,
        "model": model,
        "case_id": case_id,
        "prompt_key": prompt_key,
        "run": run,
        "workflow_complete": metrics.workflow_complete,
        "n_turns": metrics.n_turns,
        "n_llm_calls": metrics.n_llm_calls,
        "n_tool_rounds": metrics.n_tool_rounds,
        "n_tool_calls": metrics.n_tool_calls,
        "n_failed_tool_calls": metrics.n_failed_tool_calls,
        "tool_failure_rate": metrics.tool_failure_rate,
        "total_input_tokens": metrics.total_input_tokens,
        "total_output_tokens": metrics.total_output_tokens,
        "total_latency_ms": metrics.total_latency_ms,
        "hm_f1": hashmatch.f1 if hashmatch else None,
        "hm_precision": hashmatch.precision if hashmatch else None,
        "hm_recall": hashmatch.recall if hashmatch else None,
    }
    row["hashmatch"] = (
        {
            "f1": hashmatch.f1,
            "precision": hashmatch.precision,
            "recall": hashmatch.recall,
            "per_field": {k: asdict(v) for k, v in hashmatch.per_field.items()},
        }
        if hashmatch
        else None
    )
    return row


def _write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_json(rows: list[dict[str, Any]], path: Path) -> None:
    # Drop the flat hm_* columns from JSON; the nested `hashmatch` object has full detail.
    flat_only = {"hm_f1", "hm_precision", "hm_recall"}
    payload = [{k: v for k, v in row.items() if k not in flat_only} for row in rows]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(payload, fh, indent=2)
