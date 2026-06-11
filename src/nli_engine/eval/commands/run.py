"""Handler for the ``nli-eval run`` subcommand."""

from __future__ import annotations

import dataclasses
import sys
from argparse import Namespace

from rich.console import Console

from nli_engine.eval.io.parser import parse_session
from nli_engine.eval.io.report import print_run_report, write_json_report
from nli_engine.eval.scoring.metrics import compute_metrics


def cmd_run(args: Namespace) -> None:
    """Evaluate a single JSONL session log and print execution metrics.

    Args:
        args: Parsed arguments. Expected attributes: ``log`` (Path),
            ``output`` (Path | None).
    """
    console = Console()

    try:
        session_log = parse_session(args.log)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    metrics = compute_metrics(session_log)
    print_run_report(metrics, console)

    if args.output:
        write_json_report(dataclasses.asdict(metrics), args.output)
        console.print(f"[dim]Metrics written to {args.output}[/dim]")
