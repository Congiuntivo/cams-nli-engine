"""Parse JSONL session logs into structured dataclasses."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ToolCallRecord:
    """A single tool invocation recorded in the log.

    Attributes:
        tool_name: Name of the tool that was called.
        is_error: Whether the call returned an error.
        ts: Timestamp of the event.
    """

    tool_name: str
    is_error: bool
    ts: datetime


@dataclass
class StepRecord:
    """Per-step execution metrics extracted from a turn_result log entry.

    Attributes:
        step_name: Identifier of the workflow step.
        model: LLM model used, or None for non-LLM steps.
        input_tokens: Prompt tokens consumed.
        output_tokens: Completion tokens produced.
        latency_ms: Wall-clock duration of the step in milliseconds.
    """

    step_name: str
    model: str | None
    input_tokens: int
    output_tokens: int
    latency_ms: float


@dataclass
class TurnLog:
    """All events belonging to one user turn.

    Attributes:
        user_text: Raw user input text.
        tool_calls: Every tool invocation made during this turn.
        n_llm_rounds: Count of ``llm_tool_round`` events. Zero when the log
            was captured below DEBUG level.
        n_llm_calls: Count of ``llm_call`` events.
        step_logs: Per-step metrics from the ``turn_result`` entry. Empty for
            logs produced before the token-count fix was applied.
        response: Final text response from the workflow.
        done: Whether the workflow signalled completion.
        protocol: Serialized protocol dict, or None.
    """

    user_text: str
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    n_llm_rounds: int = 0
    n_llm_calls: int = 0
    step_logs: list[StepRecord] = field(default_factory=list)
    response: str = ""
    done: bool = False
    protocol: dict[str, Any] | None = None


@dataclass
class SessionLog:
    """All events from one JSONL session file.

    Attributes:
        workflow: Workflow ID used for the session.
        protocol_name: Name given to the protocol at session start.
        ts_start: Timestamp of the ``session_start`` event.
        ts_end: Timestamp of the last ``turn_result`` event, or None if the
            log contains no completed turns.
        turns: Ordered list of completed user turns.
    """

    workflow: str
    protocol_name: str
    ts_start: datetime
    ts_end: datetime | None
    turns: list[TurnLog]


def parse_session(path: Path) -> SessionLog:
    """Parse a JSONL session log file into a structured :class:`SessionLog`.

    Each line is a JSON object keyed by ``event``. Events are grouped into
    turns: a turn begins on ``user_turn`` and closes on ``turn_result``.
    Events that occur before the first ``user_turn`` (e.g. ``session_start``,
    ``workflow_config``) populate session-level fields.

    Args:
        path: Path to the ``.jsonl`` file to parse.

    Returns:
        A :class:`SessionLog` with all parsed turns.

    Raises:
        FileNotFoundError: If *path* does not exist.
        ValueError: If the log contains no ``session_start`` event.
    """
    events = _read_events(path)
    return _build_session(events)


def _read_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def _build_session(events: list[dict[str, Any]]) -> SessionLog:
    session_start = next((e for e in events if e.get("event") == "session_start"), None)
    if session_start is None:
        raise ValueError("Log contains no 'session_start' event.")

    workflow = session_start.get("workflow", "")
    protocol_name = session_start.get("protocol_name", "")
    ts_start = _parse_ts(session_start["ts"])

    turns: list[TurnLog] = []
    ts_end: datetime | None = None
    current: TurnLog | None = None

    for event in events:
        kind = event.get("event")

        if kind == "user_turn":
            current = TurnLog(user_text=event.get("text", ""))

        elif kind == "tool_call" and current is not None:
            current.tool_calls.append(
                ToolCallRecord(
                    tool_name=event["tool_name"],
                    is_error=bool(event.get("is_error", False)),
                    ts=_parse_ts(event["ts"]),
                )
            )

        elif kind == "llm_tool_round" and current is not None:
            current.n_llm_rounds += 1

        elif kind == "llm_call" and current is not None:
            current.n_llm_calls += 1

        elif kind == "turn_result" and current is not None:
            current.response = event.get("response", "")
            current.done = bool(event.get("done", False))
            current.protocol = event.get("protocol")
            current.step_logs = _parse_step_logs(event.get("logs", []))
            ts_end = _parse_ts(event["ts"])
            turns.append(current)
            current = None

    return SessionLog(
        workflow=workflow,
        protocol_name=protocol_name,
        ts_start=ts_start,
        ts_end=ts_end,
        turns=turns,
    )


def _parse_step_logs(raw: list[dict[str, Any]]) -> list[StepRecord]:
    records = []
    for entry in raw:
        records.append(
            StepRecord(
                step_name=entry.get("step_name", ""),
                model=entry.get("model"),
                input_tokens=int(entry.get("input_tokens", 0)),
                output_tokens=int(entry.get("output_tokens", 0)),
                latency_ms=float(entry.get("latency_ms", 0.0)),
            )
        )
    return records


def _parse_ts(value: str) -> datetime:
    from dateutil.parser import parse

    return parse(value)
