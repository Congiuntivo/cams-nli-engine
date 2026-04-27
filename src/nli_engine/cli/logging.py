from __future__ import annotations

import json
import logging

from rich.console import Console
from rich.markup import escape


def _truncate(s: str, n: int = 200) -> str:
    return s[:n] + "…" if len(s) > n else s


class LLMTraceHandler(logging.Handler):
    def __init__(self, console: Console, level: int = logging.DEBUG) -> None:
        super().__init__(level=level)
        self._console = console

    def emit(self, record: logging.LogRecord) -> None:
        event = getattr(record, "event", None)
        try:
            if event == "llm_call":
                self._render_llm_call(record)
            elif event == "tool_call":
                self._render_tool_call(record)
            elif event == "text_response":
                self._render_text_response_info(record)
            elif event == "llm_request":
                self._render_request(record)
            elif event == "llm_tool_round":
                self._render_tool_round(record)
            elif event == "llm_text_response":
                self._render_text_response_debug(record)
        except Exception:
            self.handleError(record)

    # ── INFO renderers (one line each) ───────────────────────────────────────

    def _render_llm_call(self, record: logging.LogRecord) -> None:
        model: str = getattr(record, "model", "?")
        self._console.print(f"[dim]→ llm[/dim]  [cyan]{escape(model)}[/cyan]")

    def _render_tool_call(self, record: logging.LogRecord) -> None:
        name: str = getattr(record, "tool_name", "?")
        self._console.print(f"[dim]↳[/dim] [cyan]{escape(name)}[/cyan]")

    def _render_text_response_info(self, record: logging.LogRecord) -> None:
        text: str = getattr(record, "text", "")
        self._console.print(f'[dim]←[/dim] "{escape(_truncate(text, 120))}"')

    # ── DEBUG renderers (full blocks) ────────────────────────────────────────

    def _render_request(self, record: logging.LogRecord) -> None:
        model: str = getattr(record, "model", "?")
        messages: list[dict] = getattr(record, "messages", [])
        n_tools: int = getattr(record, "n_tools", 0)

        self._console.print(
            f"[dim]┌─[/dim] [bold]llm[/bold] [dim]·[/dim] [cyan]{escape(model)}[/cyan]"
            f" [dim]·[/dim] {len(messages)} msgs [dim]·[/dim] {n_tools} tools"
        )
        for msg in messages:
            role = msg.get("role", "?")
            raw = msg.get("content") or ""
            if isinstance(raw, list):
                raw = json.dumps(raw)
            content = escape(_truncate(str(raw)))
            self._console.print(f"[dim]│  {role}:[/dim] {content}")
        self._console.print("[dim]└─[/dim]")

    def _render_tool_round(self, record: logging.LogRecord) -> None:
        tool_calls: list[dict] = getattr(record, "tool_calls", [])
        self._console.print(
            f"[dim]┌─[/dim] [bold]response[/bold] [dim]·[/dim] {len(tool_calls)} tool calls"
        )
        for tc in tool_calls:
            name = escape(tc.get("name", "?"))
            args = escape(_truncate(json.dumps(tc.get("arguments", {}))))
            result = escape(_truncate(str(tc.get("result", ""))))
            self._console.print(
                f"[dim]│[/dim]  [dim]↳[/dim] [cyan]{name}[/cyan]({args}) [dim]→[/dim] {result}"
            )
        self._console.print("[dim]└─[/dim]")

    def _render_text_response_debug(self, record: logging.LogRecord) -> None:
        text: str = getattr(record, "text", "")
        self._console.print("[dim]┌─[/dim] [bold]response[/bold] [dim]·[/dim] text")
        self._console.print(f'[dim]│[/dim]  "{escape(_truncate(text))}"')
        self._console.print("[dim]└─[/dim]")


def configure_verbose_logging(console: Console, level: int = logging.DEBUG) -> None:
    logger = logging.getLogger("nli_engine.llm")
    logger.addHandler(LLMTraceHandler(console, level=level))
    logger.setLevel(level)
