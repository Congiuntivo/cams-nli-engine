"""Entry point for the nli-eval command-line tool."""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

from rich.console import Console

from nli_engine.eval.dataset import (
    evaluate_dataset,
    load_manifest,
    resolve_from_log,
    resolve_last_from,
)
from nli_engine.eval.metrics import compute_metrics
from nli_engine.eval.parser import parse_session
from nli_engine.eval.report import (
    print_comparison_report,
    print_dataset_report,
    print_run_report,
    write_json_report,
)


def main() -> None:
    """Entry point for the ``nli-eval`` CLI."""
    parser = _build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    # Call the handler function associated with the chosen subcommand, passing the parsed args.
    args.func(args)


def _build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="nli-eval",
        description="Evaluate NLI engine session logs.",
    )
    subs = root.add_subparsers(title="subcommands")

    run_parser = subs.add_parser(
        "run",
        help="Evaluate a single JSONL session log.",
    )
    run_parser.add_argument(
        "log", type=Path, metavar="LOG", help="Path to the .jsonl log file."
    )
    run_parser.add_argument(
        "--output",
        type=Path,
        metavar="PATH",
        help="Write metrics as JSON to this file.",
    )
    run_parser.set_defaults(func=_cmd_run)

    dataset_parser = subs.add_parser(
        "dataset",
        help="Evaluate all cases in a manifest YAML file.",
    )
    dataset_parser.add_argument(
        "manifest",
        type=Path,
        metavar="MANIFEST",
        help="Path to the manifest .yaml file.",
    )
    dataset_parser.add_argument(
        "--output",
        type=Path,
        metavar="PATH",
        help="Write full results as JSON to this file.",
    )
    dataset_parser.add_argument(
        "log",
        type=Path,
        metavar="LOG",
        nargs="?",
        default=None,
        help="Path to a single .jsonl log file to evaluate (mutually exclusive with --last-from).",
    )
    dataset_parser.add_argument(
        "--last-from",
        type=Path,
        metavar="LOGS_DIR",
        dest="last_from",
        help=(
            "Directory of .jsonl log files. For each manifest prompt, find the "
            "most recent file whose user_turn matches and evaluate it."
        ),
    )
    dataset_parser.set_defaults(func=_cmd_dataset)

    extract_parser = subs.add_parser(
        "extract",
        help="Extract the final protocol from a JSONL session log.",
    )
    extract_parser.add_argument(
        "log", type=Path, metavar="LOG", help="Path to the .jsonl log file."
    )
    extract_parser.add_argument(
        "output", type=Path, metavar="OUTPUT", help="Path to write the protocol JSON."
    )
    extract_parser.set_defaults(func=_cmd_extract)

    return root


def _cmd_run(args: argparse.Namespace) -> None:
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


def _cmd_dataset(args: argparse.Namespace) -> None:
    console = Console()

    try:
        cases = load_manifest(args.manifest)
        if args.log is not None:
            resolved = [resolve_from_log(cases, args.log)]
        elif args.last_from is not None:
            resolved = resolve_last_from(cases, args.last_from)
        else:
            console.print("[red]Error:[/red] Provide either a LOG path or --last-from.")
            sys.exit(1)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    results = evaluate_dataset(resolved)
    print_dataset_report(results, console)

    for result in results:
        if result.comparison is not None:
            console.rule(f"[cyan]{result.case_id} / {result.prompt_key}[/cyan]")
            print_comparison_report(result.comparison, console)

    if args.output:
        write_json_report([dataclasses.asdict(r) for r in results], args.output)
        console.print(f"[dim]Results written to {args.output}[/dim]")


def _cmd_extract(args: argparse.Namespace) -> None:
    console = Console()

    try:
        session_log = parse_session(args.log)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    turns_with_protocol = [t for t in session_log.turns if t.protocol is not None]
    if not turns_with_protocol:
        console.print("[red]Error:[/red] No protocol found in session log.")
        sys.exit(1)

    protocol = turns_with_protocol[-1].protocol
    args.output.write_text(json.dumps(protocol, indent=2))
    console.print(f"[dim]Protocol written to {args.output}[/dim]")
