import argparse

from nli_engine.engine.workflow.registry import WORKFLOW_REGISTRY
from nli_engine.cli.interactive import run_interactive


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nli-engine",
        description="Natural-language interface for authoring CARP study protocols.",
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "non-interactive"],
        default="interactive",
        help="Run mode (default: interactive).",
    )
    parser.add_argument(
        "--workflow",
        metavar="ID",
        default=None,
        help=f"Workflow to run. Available: {', '.join(WORKFLOW_REGISTRY)}.",
    )
    parser.add_argument(
        "--server",
        metavar="URL",
        default="http://localhost:8080",
        help="Authoring server base URL (default: http://localhost:8080).",
    )
    parser.add_argument(
        "--config",
        metavar="PATH",
        default=None,
        help="Path to a workflow YAML config file. Uses defaults if omitted.",
    )
    return parser


def run() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.mode == "non-interactive":
        raise NotImplementedError("Non-interactive mode is not yet implemented.")

    run_interactive(args)
