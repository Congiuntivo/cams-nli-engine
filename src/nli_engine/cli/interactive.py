from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from nli_engine.engine.client import build_client
from nli_engine.engine.conversation import Conversation
from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.registry import WORKFLOW_REGISTRY, WorkflowSpec

console = Console()


def _select_workflow(preselected_id: str | None) -> WorkflowSpec:
    if preselected_id is not None:
        spec = WORKFLOW_REGISTRY.get(preselected_id)
        if spec is None:
            console.print(
                f"[red]Unknown workflow '[bold]{preselected_id}[/bold]'. "
                f"Available: {', '.join(WORKFLOW_REGISTRY)}[/red]"
            )
            raise SystemExit(1)
        return spec

    table = Table(title="Available workflows", show_lines=False, highlight=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("ID", style="bold cyan")
    table.add_column("Name")
    table.add_column("Description", style="dim")

    specs = list(WORKFLOW_REGISTRY.values())
    for i, spec in enumerate(specs, start=1):
        table.add_row(str(i), spec.id, spec.name, spec.description)
    console.print(table)

    choices = [str(i) for i in range(1, len(specs) + 1)] + list(WORKFLOW_REGISTRY)
    raw = Prompt.ask("Select workflow", choices=choices, show_choices=False)
    if raw.isdigit():
        return specs[int(raw) - 1]
    return WORKFLOW_REGISTRY[raw]


def _show_logs(logs: list) -> None:
    if not logs:
        return
    table = Table(show_header=True, header_style="dim", box=None)
    table.add_column("step", style="dim")
    table.add_column("model", style="dim")
    table.add_column("latency", style="dim", justify="right")
    for log in logs:
        table.add_row(
            log.step_name,
            log.model or "—",
            f"{log.latency_ms:.1f}ms",
        )
    console.print(table)


def run_interactive(args: argparse.Namespace) -> None:
    config = WorkflowConfig.from_yaml(args.config) if args.config else WorkflowConfig()

    try:
        spec = _select_workflow(args.workflow)
        protocol_name = Prompt.ask("[bold]Protocol name[/bold]")
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Bye.[/dim]")
        return

    session = ProtocolSession(build_client(args.server), name=protocol_name)
    conversation = Conversation(spec, config, session)

    console.print(
        f"\n[dim]Workflow:[/dim] [bold cyan]{spec.name}[/bold cyan]  "
        f"[dim]· type [bold]exit[/bold] or press Ctrl-C to quit[/dim]\n"
    )

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]>[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Bye.[/dim]")
            break

        if user_input.strip().lower() in {"exit", "quit"}:
            console.print("[dim]Bye.[/dim]")
            break

        result = conversation.turn(user_input)
        console.print(
            Panel(result.message, title="[bold]response[/bold]", border_style="cyan")
        )
        if result.protocol is not None:
            import json

            console.print(
                Panel(
                    json.dumps(result.protocol, indent=2),
                    title="[bold]protocol[/bold]",
                    border_style="dim",
                )
            )
        _show_logs(result.logs)
        if result.done:
            console.print("[dim]Workflow complete.[/dim]")
            break
