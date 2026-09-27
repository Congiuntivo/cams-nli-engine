from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from nli_engine.cli.logging import (
    configure_file_logging,
    configure_verbose_logging,
    initialize_trace_loggers,
)
from nli_engine.engine.client import build_client
from nli_engine.engine.conversation import Conversation
from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.registry import WORKFLOW_REGISTRY, WorkflowSpec
from nli_engine.engine.workflow.result import TurnResult

_session_log = logging.getLogger("nli_engine.session")


def _get_git_commit_hash() -> str:
    """Return the current Git commit hash, or 'unknown' if it can't be determined."""
    try:
        import subprocess

        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


class InteractiveCLI:
    """Drives the interactive prompt-response loop for the NLI engine CLI."""

    def __init__(self) -> None:
        self.console = Console()

    def run(self, args: argparse.Namespace) -> None:
        """Configure, set up the session, and start the conversation loop.

        Args:
            args: Parsed CLI arguments. Relevant fields: ``workflow``, ``server``,
                ``config``, ``verbose`` (0 = silent, 1 = INFO, 2 = DEBUG),
                ``name`` (skips the protocol-name prompt), ``prompt``
                (fires the first turn automatically), and ``log_output``
                (path to a JSON Lines session log).
        """
        initialize_trace_loggers()
        self._configure_verbosity(args)
        if args.log_output:
            configure_file_logging(Path(args.log_output))
        config = (
            WorkflowConfig.from_yaml(args.config) if args.config else WorkflowConfig()
        )
        if args.stop_after:
            config = config.model_copy(
                update={
                    "parameters": {**config.parameters, "stop_after": args.stop_after}
                }
            )

        try:
            spec = self._select_workflow(args.workflow)
            protocol_name = args.name or Prompt.ask("[bold]Protocol name[/bold]")
        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[dim]Bye.[/dim]")
            return

        _session_log.info(
            "session_start",
            extra={
                "event": "session_start",
                "workflow": spec.id,
                "protocol_name": protocol_name,
            },
        )
        _session_log.info(
            "workflow_config",
            extra={
                "event": "workflow_config",
                "config": config.model_dump(),
                "nli_engine_git_hash": _get_git_commit_hash(),
            },
        )
        session = ProtocolSession(build_client(args.server), name=protocol_name)
        conversation = Conversation(spec, config, session)
        self._run_loop(conversation, spec, initial_prompt=args.prompt)

    def _select_workflow(self, preselected_id: str | None) -> WorkflowSpec:
        """Return the workflow spec for the given ID, or prompt the user to choose."""
        if preselected_id is not None:
            spec = WORKFLOW_REGISTRY.get(preselected_id)
            if spec is None:
                self.console.print(
                    f"[red]Unknown workflow '[bold]{preselected_id}[/bold]'. "
                    f"Available: {', '.join(WORKFLOW_REGISTRY)}[/red]"
                )
                raise SystemExit(1)
            return spec

        self.console.print(self._build_workflow_table())
        specs = list(WORKFLOW_REGISTRY.values())
        choices = [str(i) for i in range(1, len(specs) + 1)] + list(WORKFLOW_REGISTRY)
        raw = Prompt.ask("Select workflow", choices=choices, show_choices=False)
        if raw.isdigit():
            return specs[int(raw) - 1]
        return WORKFLOW_REGISTRY[raw]

    def _build_workflow_table(self) -> Table:
        """Build a Rich table listing all registered workflows."""
        table = Table(title="Available workflows", show_lines=False, highlight=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("ID", style="bold cyan")
        table.add_column("Name")
        table.add_column("Description", style="dim")
        for i, spec in enumerate(WORKFLOW_REGISTRY.values(), start=1):
            table.add_row(str(i), spec.id, spec.name, spec.description)
        return table

    def _run_loop(
        self,
        conversation: Conversation,
        spec: WorkflowSpec,
        initial_prompt: str | None = None,
    ) -> None:
        """Drive the prompt-response loop until the user exits or the workflow completes.

        Args:
            conversation: Active conversation to send turns to.
            spec: Workflow spec used for the header line.
            initial_prompt: Optional first turn sent automatically before entering
                the interactive loop; useful for scripted or repeated test runs.
        """
        self.console.print(
            f"\n[dim]Workflow:[/dim] [bold cyan]{spec.name}[/bold cyan]  "
            f"[dim]· type [bold]exit[/bold] or press Ctrl-C to quit[/dim]\n"
        )

        if initial_prompt is not None:
            self.console.print(f"[bold cyan]>[/bold cyan] [dim]{initial_prompt}[/dim]")
            result = self._execute_turn(conversation, initial_prompt)
            self._display_result(result)
            if result.done:
                self.console.print("[dim]Workflow complete.[/dim]")
                return

        while True:
            try:
                user_input = Prompt.ask("[bold cyan]>[/bold cyan]")
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[dim]Bye.[/dim]")
                break

            if user_input.strip().lower() in {"exit", "quit"}:
                self.console.print("[dim]Bye.[/dim]")
                break

            result = self._execute_turn(conversation, user_input)
            self._display_result(result)
            if result.done:
                self.console.print("[dim]Workflow complete.[/dim]")
                break

    def _execute_turn(self, conversation: Conversation, user_input: str) -> TurnResult:
        """Send one user turn, emit session log events, and return the result.

        Any exception raised by the workflow is captured, logged as an
        ``llm_error`` event, and re-raised as ``SystemExit(1)`` with a compact
        one-line summary. This keeps the JSONL log terminated cleanly and
        avoids flooding stderr with a raw traceback that a downstream
        parser can't do anything with.
        """
        _session_log.info("user_turn", extra={"event": "user_turn", "text": user_input})
        try:
            result = conversation.turn(user_input)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            _session_log.error(
                "interrupted",
                extra={"event": "interrupted", "reason": "SIGINT"},
            )
            self.console.print("\n[yellow]interrupted[/yellow]")
            raise SystemExit(130)
        except Exception as exc:
            _session_log.error(
                "llm_error",
                extra={
                    "event": "llm_error",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
            )
            self.console.print(
                f"[red]workflow_error[/red] {type(exc).__name__}: {exc}",
                soft_wrap=True,
            )
            raise SystemExit(1) from exc
        _session_log.info(
            "turn_result",
            extra={
                "event": "turn_result",
                "response": result.message,
                "protocol": result.protocol,
                "done": result.done,
                "logs": [log.model_dump() for log in result.logs],
            },
        )
        return result

    def _display_result(self, result: TurnResult) -> None:
        """Print the response message, optional protocol JSON, and step logs."""
        self.console.print(
            Panel(result.message, title="[bold]response[/bold]", border_style="cyan")
        )
        if result.protocol is not None:
            self.console.print(
                Panel(
                    json.dumps(result.protocol, indent=2),
                    title="[bold]protocol[/bold]",
                    border_style="dim",
                )
            )
        self._show_logs(result.logs)

    def _show_logs(self, logs: list) -> None:
        """Print a table of per-step latency and model information."""
        if not logs:
            return
        table = Table(show_header=True, header_style="dim", box=None)
        table.add_column("step", style="dim")
        table.add_column("model", style="dim")
        table.add_column("latency", style="dim", justify="right")
        for log in logs:
            table.add_row(log.step_name, log.model or "—", f"{log.latency_ms:.1f}ms")
        self.console.print(table)

    def _configure_verbosity(self, args: argparse.Namespace) -> None:
        """Set up logging handlers based on the --verbose flag count."""
        verbosity: int = getattr(args, "verbose", 0)
        if verbosity >= 1:
            level = logging.INFO if verbosity == 1 else logging.DEBUG
            configure_verbose_logging(self.console, level)
