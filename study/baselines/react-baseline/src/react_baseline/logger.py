"""JSONL event emitter that matches the schema consumed by ``nli-eval``.

Only the events read by ``nli_engine.eval.io.parser`` are emitted:
``session_start``, ``user_turn``, ``tool_call``, ``llm_call``,
``llm_tool_round``, ``turn_result``. Additional fields are ignored by the
parser and therefore omitted.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


class SessionLogger:
    """Append-only JSONL writer for a single baseline cell."""

    def __init__(self, path: Path) -> None:
        """Open ``path`` for append.

        Args:
            path: Destination JSONL file. Parent directories must exist.
        """
        self._path = path
        self._fh = path.open("w")

    def _write(self, event: dict[str, Any]) -> None:
        event = {"ts": _ts(), **event}
        self._fh.write(json.dumps(event) + "\n")
        self._fh.flush()

    def session_start(self, workflow: str, protocol_name: str) -> None:
        """Emit the ``session_start`` event."""
        self._write(
            {
                "event": "session_start",
                "workflow": workflow,
                "protocol_name": protocol_name,
            }
        )

    def user_turn(self, text: str) -> None:
        """Emit the ``user_turn`` event."""
        self._write({"event": "user_turn", "text": text})

    def llm_call(self, model: str) -> None:
        """Emit an ``llm_call`` event (counted by the aggregate)."""
        self._write({"event": "llm_call", "model": model})

    def llm_tool_round(self, tool_calls: list[dict[str, Any]]) -> None:
        """Emit an ``llm_tool_round`` event for one batch of tool calls."""
        self._write({"event": "llm_tool_round", "tool_calls": tool_calls})

    def tool_call(self, tool_name: str, is_error: bool) -> None:
        """Emit a ``tool_call`` event for a single tool invocation."""
        self._write(
            {
                "event": "tool_call",
                "tool_name": tool_name,
                "is_error": is_error,
            }
        )

    def turn_result(
        self,
        response: str,
        done: bool,
        protocol: dict[str, Any] | None,
        step_logs: list[dict[str, Any]],
    ) -> None:
        """Emit the terminating ``turn_result`` event.

        Args:
            response: Final assistant text.
            done: Whether the workflow completed (a successful serialize).
            protocol: Serialized protocol dict, or ``None`` if unavailable.
            step_logs: Per-step metrics list. The baseline emits a single
                aggregate entry with total tokens and wall-clock latency.
        """
        self._write(
            {
                "event": "turn_result",
                "response": response,
                "done": done,
                "protocol": protocol,
                "logs": step_logs,
            }
        )

    def close(self) -> None:
        """Close the underlying file handle."""
        self._fh.close()

    def __enter__(self) -> "SessionLogger":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
