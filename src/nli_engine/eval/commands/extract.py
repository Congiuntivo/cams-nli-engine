"""Handler for the ``nli-eval extract`` subcommand."""

from __future__ import annotations

import json
import sys
from argparse import Namespace

from rich.console import Console

from nli_engine.eval.io.parser import parse_session


def cmd_extract(args: Namespace) -> None:
    """Extract the final protocol from a JSONL session log and write it as JSON.

    Args:
        args: Parsed arguments. Expected attributes: ``log`` (Path),
            ``output`` (Path).
    """
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
