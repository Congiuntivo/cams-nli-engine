from __future__ import annotations

import json
import logging

from rich.console import Console
from rich.markup import escape


def _truncate(s: str, n: int = 200, remove_new_lines: bool = True) -> str:
    """Truncate a string to at most n characters, adding an ellipsis if truncated.

    Args:
        s: The string to truncate.
        n: The maximum length of the string. Default is 200 characters.
        remove_new_lines: If True, replace new line characters with spaces.

    Returns:
        The truncated string, with new lines replaced if specified.
    """
    if remove_new_lines:
        s = s.replace("\n", " ")
    return s[:n] + "…" if len(s) > n else s


class TraceHandler(logging.Handler):
    """Logging handler that renders structured trace events to a Rich console.

    Handles step lifecycle events emitted by ``Step.run``: ``step_begin`` and
    ``step_end`` at INFO level. Also handles six LLM trace events emitted by
    ``LLMStep``: ``llm_call``, ``tool_call``, and ``text_response`` at INFO
    level (one-liners), and ``llm_request``, ``llm_tool_round``, and
    ``llm_text_response`` at DEBUG level (full blocks).
    """

    def __init__(self, console: Console, level: int = logging.DEBUG) -> None:
        """
        Args:
            console: Rich console used for output.
            level: Minimum log level to handle. Use ``logging.INFO`` for
                one-line events or ``logging.DEBUG`` for full trace blocks.
        """
        super().__init__(level=level)
        self._console = console

    def emit(self, record: logging.LogRecord) -> None:
        event = getattr(record, "event", None)
        try:
            if event == "step_begin":
                self._render_step_begin(record)
            elif event == "step_end":
                self._render_step_end(record)
            elif event == "llm_call":
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

    def _render_step_begin(self, record: logging.LogRecord) -> None:
        step_name: str = getattr(record, "step_name", "?")
        self._console.print(f"[dim]▶ step [/dim][cyan]{escape(step_name)}[/cyan]")

    def _render_step_end(self, record: logging.LogRecord) -> None:
        step_name: str = getattr(record, "step_name", "?")
        self._console.print(f"[dim]◀ step [/dim][cyan]{escape(step_name)}[/cyan]")

    def _render_llm_call(self, record: logging.LogRecord) -> None:
        model: str = getattr(record, "model", "?")
        self._console.print(f"[dim]→ LLM call [/dim][cyan]{escape(model)}[/cyan]")

    def _render_tool_call(self, record: logging.LogRecord) -> None:
        name: str = getattr(record, "tool_name", "?")
        failed: bool = getattr(record, "is_error", False)
        self._console.print(
            f"\t[dim]↳[/dim] Tool usage: [cyan]{escape(name)}[/cyan]"
            + (" [red](failed)[/red]" if failed else "")
        )

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
            f"\t[dim]┌─[/dim] [bold]response[/bold] [dim]·[/dim] {len(tool_calls)} tool calls"
        )
        for tc in tool_calls:
            name = escape(tc.get("name", "?"))
            args = escape(_truncate(json.dumps(tc.get("arguments", {}))))
            result = escape(_truncate(str(tc.get("result", ""))))
            is_error = tc.get("is_error", False)
            result_markup = f"[red]{result}[/red]" if is_error else result
            self._console.print(
                f"\t[dim]│[/dim]  [dim]↳[/dim] [cyan]{name}[/cyan]({args}) [dim]→[/dim] {result_markup}"
            )
        self._console.print("\t[dim]└─[/dim]")

    def _render_text_response_debug(self, record: logging.LogRecord) -> None:
        text: str = getattr(record, "text", "")
        self._console.print("[dim]┌─[/dim] [bold]response[/bold] [dim]·[/dim] text")
        self._console.print(f'[dim]│[/dim]  "{escape(_truncate(text))}"')
        self._console.print("[dim]└─[/dim]")


def configure_verbose_logging(console: Console, level: int = logging.DEBUG) -> None:
    """Attach a TraceHandler to the ``nli_engine.step`` and ``nli_engine.llm`` loggers.

    Logger levels are managed externally by ``initialize_trace_loggers``; this
    function only registers the handler at the requested filter level.

    Args:
        console: Rich console for trace output.
        level: ``logging.INFO`` for one-line events, ``logging.DEBUG`` for
            full trace blocks.
    """
    handler = TraceHandler(console, level=level)
    for name in ("nli_engine.step", "nli_engine.llm"):
        logging.getLogger(name).addHandler(handler)
