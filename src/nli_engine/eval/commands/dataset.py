"""Handler for the ``nli-eval dataset`` subcommand."""

from __future__ import annotations

import dataclasses
import sys
from argparse import Namespace

from rich.console import Console

from nli_engine.eval.io.dataset import (
    evaluate_dataset,
    load_manifest,
    resolve_from_log,
    resolve_last_from,
)
from nli_engine.eval.io.report import (
    print_comparison_report,
    print_dataset_report,
    write_json_report,
)


def cmd_dataset(args: Namespace) -> None:
    """Evaluate all cases in a manifest YAML file.

    Args:
        args: Parsed arguments. Expected attributes: ``manifest`` (Path),
            ``log`` (Path | None), ``last_from`` (Path | None),
            ``output`` (Path | None).
    """
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
