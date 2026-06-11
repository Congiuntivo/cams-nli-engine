"""Entry point for the nli-eval command-line tool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nli_engine.eval.commands.canonicalize import cmd_canonicalize
from nli_engine.eval.commands.dataset import cmd_dataset
from nli_engine.eval.commands.extract import cmd_extract
from nli_engine.eval.commands.run import cmd_run


def main() -> None:
    """Entry point for the ``nli-eval`` CLI."""
    parser = _build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

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
    run_parser.set_defaults(func=cmd_run)

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
    dataset_parser.set_defaults(func=cmd_dataset)

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
    extract_parser.set_defaults(func=cmd_extract)

    canon_parser = subs.add_parser(
        "canonicalize",
        help="Dump content-addressed protocol JSON for diffing.",
    )
    canon_parser.add_argument(
        "files",
        type=Path,
        metavar="FILE",
        nargs="+",
        help="One or two protocol .json files or .jsonl session logs.",
    )
    canon_parser.add_argument(
        "--output",
        type=Path,
        metavar="PATH",
        help="(single-file mode) Write canonicalized JSON to this file instead of stdout.",
    )
    canon_parser.add_argument(
        "--out-dir",
        type=Path,
        metavar="DIR",
        dest="out_dir",
        help="(two-file mode) Directory to write both canonicalized files. Defaults to '.'.",
    )
    canon_parser.set_defaults(func=cmd_canonicalize)

    return root
