"""Handler for the ``nli-eval canonicalize`` subcommand."""

from __future__ import annotations

import copy
import json
import sys
from argparse import Namespace
from pathlib import Path

from rich.console import Console

from nli_engine.eval.io.parser import parse_session
from nli_engine.eval.scoring.hashmatch import to_content_addressed


def cmd_canonicalize(args: Namespace) -> None:
    """Dump content-addressed protocol JSON for diffing.

    Accepts one or two files (.json or .jsonl). A .jsonl input is treated as a
    session log and the final protocol is extracted before canonicalization.
    One-file mode writes to stdout or --output; two-file mode writes both
    outputs to --out-dir.

    Args:
        args: Parsed arguments. Expected attributes: ``files`` (list[Path]),
            ``output`` (Path | None), ``out_dir`` (Path | None).
    """
    console = Console()

    if len(args.files) > 2:
        console.print("[red]Error:[/red] At most two files may be given.")
        sys.exit(1)

    try:
        protocols = [_load_protocol(p) for p in args.files]
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    canonicalized = [to_content_addressed(copy.deepcopy(p)) for p in protocols]

    if len(args.files) == 1:
        text = json.dumps(canonicalized[0], indent=2)
        if args.output:
            args.output.write_text(text)
            console.print(f"[dim]Written to {args.output}[/dim]")
        else:
            print(text)
    else:
        out_dir = args.out_dir or Path(".")
        out_dir.mkdir(parents=True, exist_ok=True)
        for src_path, ca in zip(args.files, canonicalized):
            out_path = out_dir / src_path.with_suffix(".json").name
            out_path.write_text(json.dumps(ca, indent=2))
            console.print(f"[dim]Written to {out_path}[/dim]")


def _load_protocol(path: Path) -> dict:
    """Load a protocol dict from a .jsonl session log or a .json file."""
    if path.suffix == ".jsonl":
        session_log = parse_session(path)
        turns_with_protocol = [t for t in session_log.turns if t.protocol is not None]
        if not turns_with_protocol:
            raise ValueError(f"No protocol found in session log: {path}")
        return turns_with_protocol[-1].protocol
    with path.open() as fh:
        return json.load(fh)
