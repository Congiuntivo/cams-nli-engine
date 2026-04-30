import argparse

from nli_engine.cli.interactive import InteractiveCLI
from nli_engine.engine.workflow.registry import WORKFLOW_REGISTRY


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
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="-v for minimal trace, -vv for full debug trace.",
    )
    return parser


def run() -> None:
    """Parse CLI arguments and dispatch to the appropriate run mode."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.mode == "non-interactive":
        raise NotImplementedError("Non-interactive mode is not yet implemented.")

    InteractiveCLI().run(args)
