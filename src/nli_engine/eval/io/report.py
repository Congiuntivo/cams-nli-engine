"""Rich table rendering and JSON file output for evaluation results."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from nli_engine.eval.io.dataset import CaseResult
from nli_engine.eval.scoring.comparison import ComparisonResult
from nli_engine.eval.scoring.metrics import SessionMetrics


def print_run_report(
    metrics: SessionMetrics, console: Console, latency_seconds: bool = True
) -> None:
    """Print a single-run metrics table to *console*.

    Args:
        metrics: Metrics computed from one session log.
        console: Rich Console to write to.
    """
    table = Table(title="Session metrics", show_header=True, header_style="bold")
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")

    complete_str = (
        "[green]yes[/green]" if metrics.workflow_complete else "[red]no[/red]"
    )

    rows: list[tuple[str, str]] = [
        ("workflow_complete", complete_str),
        ("n_turns", str(metrics.n_turns)),
        ("n_llm_calls", str(metrics.n_llm_calls)),
        ("n_tool_rounds", str(metrics.n_tool_rounds)),
        ("n_tool_calls", str(metrics.n_tool_calls)),
        ("n_failed_tool_calls", str(metrics.n_failed_tool_calls)),
        ("tool_failure_rate", f"{metrics.tool_failure_rate:.1%}"),
        ("n_unique_tools", str(metrics.n_unique_tools)),
        ("total_input_tokens", str(metrics.total_input_tokens)),
        ("total_output_tokens", str(metrics.total_output_tokens)),
        (
            "total_latency_s" if latency_seconds else "total_latency_ms",
            (
                f"{metrics.total_latency_ms / 1000:.2f}"
                if latency_seconds
                else f"{metrics.total_latency_ms:,.1f}"
            ),
        ),
    ]
    for name, value in rows:
        table.add_row(name, value)

    console.print(table)

    if metrics.unique_tools_used:
        console.print(
            "[dim]tools used:[/dim] " + ", ".join(sorted(metrics.unique_tools_used))
        )


def print_comparison_report(comparison: ComparisonResult, console: Console) -> None:
    """Print a per-field HashMatch breakdown table to *console*.

    Args:
        comparison: Comparison result containing a :class:`~nli_engine.eval.scoring.hashmatch.HashMatchScore`.
        console: Rich Console to write to.
    """
    hm = comparison.hashmatch
    table = Table(title="HashMatch per-field", show_header=True, header_style="bold")
    table.add_column("Field", style="cyan")
    table.add_column("F1", justify="right")
    table.add_column("P", justify="right")
    table.add_column("R", justify="right")
    table.add_column("TP", justify="right")
    table.add_column("FP", justify="right")
    table.add_column("FN", justify="right")

    for field, score in sorted(hm.per_field.items()):
        table.add_row(
            field,
            f"{score.f1:.1%}",
            f"{score.precision:.1%}",
            f"{score.recall:.1%}",
            str(score.tp),
            str(score.fp),
            str(score.fn),
        )

    table.add_section()
    table.add_row(
        "[bold]macro avg[/bold]",
        f"[bold]{hm.f1:.1%}[/bold]",
        f"[bold]{hm.precision:.1%}[/bold]",
        f"[bold]{hm.recall:.1%}[/bold]",
        "",
        "",
        "",
    )

    console.print(table)


def print_dataset_report(results: list[CaseResult], console: Console) -> None:
    """Print a per-case summary table for a dataset evaluation.

    Args:
        results: List of :class:`~nli_engine.eval.io.dataset.CaseResult` objects.
        console: Rich Console to write to.
    """
    table = Table(title="Dataset evaluation", show_header=True, header_style="bold")
    table.add_column("Case", style="cyan")
    table.add_column("Complete", justify="center")
    table.add_column("Tools", justify="right")
    table.add_column("Failed", justify="right")
    table.add_column("Tokens (in+out)", justify="right")
    table.add_column("Latency (ms)", justify="right")
    table.add_column("HM precision", justify="right")
    table.add_column("HM recall", justify="right")
    table.add_column("HM F1", justify="right")

    for result in results:
        m = result.metrics
        hm = result.comparison.hashmatch if result.comparison else None
        complete_str = "[green]✓[/green]" if m.workflow_complete else "[red]✗[/red]"
        tokens_str = f"{m.total_input_tokens}+{m.total_output_tokens}"
        precision_str = f"{hm.precision:.1%}" if hm else "—"
        recall_str = f"{hm.recall:.1%}" if hm else "—"
        f1_str = f"{hm.f1:.1%}" if hm else "—"

        table.add_row(
            f"{result.case_id} / {result.prompt_key}",
            complete_str,
            str(m.n_tool_calls),
            str(m.n_failed_tool_calls),
            tokens_str,
            f"{m.total_latency_ms:,.1f}",
            precision_str,
            recall_str,
            f1_str,
        )

    console.print(table)


def write_json_report(data: Any, path: Path) -> None:
    """Serialize *data* to a JSON file at *path*.

    Dataclasses, frozensets, and Paths are handled automatically.

    Args:
        data: Any JSON-serializable object (dataclasses are converted via
            :func:`dataclasses.asdict` before writing).
        path: Destination file path; parent directories must exist.
    """
    with path.open("w") as fh:
        json.dump(data, fh, indent=2, default=_json_default)


def _json_default(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    if isinstance(obj, frozenset):
        return sorted(obj)
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
