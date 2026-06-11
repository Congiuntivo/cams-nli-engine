"""Compute execution metrics from a parsed session log."""

from __future__ import annotations

from dataclasses import dataclass

from nli_engine.eval.io.parser import SessionLog


@dataclass(frozen=True)
class SessionMetrics:
    """Execution metrics derived from a single session log.

    Attributes:
        n_turns: Number of completed user turns.
        n_llm_calls: Total LLM completions across all turns.
        n_tool_rounds: Total agentic loop iterations (``llm_tool_round``
            events). Zero when the log was captured below DEBUG level.
        n_tool_calls: Total tool invocations across all turns.
        n_failed_tool_calls: Tool invocations that returned an error.
        tool_failure_rate: ``n_failed_tool_calls / n_tool_calls``, or 0.0
            when no tools were called.
        unique_tools_used: Distinct tool names called during the session.
        n_unique_tools: Cardinality of ``unique_tools_used``.
        total_input_tokens: Sum of prompt tokens across all steps. Zero for
            logs produced before token counts were added to the log format.
        total_output_tokens: Sum of completion tokens across all steps.
        total_latency_ms: Wall-clock duration from ``session_start`` to the
            last ``turn_result``. Zero if the log contains no completed turns.
        workflow_complete: Whether the last turn signalled ``done=True``.
    """

    n_turns: int
    n_llm_calls: int
    n_tool_rounds: int
    n_tool_calls: int
    n_failed_tool_calls: int
    tool_failure_rate: float
    unique_tools_used: frozenset[str]
    n_unique_tools: int
    total_input_tokens: int
    total_output_tokens: int
    total_latency_ms: float
    workflow_complete: bool


def compute_metrics(session: SessionLog) -> SessionMetrics:
    """Compute :class:`SessionMetrics` from a parsed session log.

    Args:
        session: A :class:`~nli_engine.eval.io.parser.SessionLog` returned by
            :func:`~nli_engine.eval.io.parser.parse_session`.

    Returns:
        A frozen :class:`SessionMetrics` dataclass.
    """
    n_llm_calls = sum(t.n_llm_calls for t in session.turns)
    n_tool_rounds = sum(t.n_llm_rounds for t in session.turns)

    all_tool_calls = [tc for t in session.turns for tc in t.tool_calls]
    n_tool_calls = len(all_tool_calls)
    n_failed = sum(1 for tc in all_tool_calls if tc.is_error)
    tool_failure_rate = n_failed / n_tool_calls if n_tool_calls > 0 else 0.0
    unique_tools = frozenset(tc.tool_name for tc in all_tool_calls)

    all_steps = [sr for t in session.turns for sr in t.step_logs]
    total_input = sum(s.input_tokens for s in all_steps)
    total_output = sum(s.output_tokens for s in all_steps)

    if session.ts_end is not None:
        delta = session.ts_end - session.ts_start
        total_latency_ms = delta.total_seconds() * 1000.0
    else:
        total_latency_ms = 0.0

    workflow_complete = session.turns[-1].done if session.turns else False

    return SessionMetrics(
        n_turns=len(session.turns),
        n_llm_calls=n_llm_calls,
        n_tool_rounds=n_tool_rounds,
        n_tool_calls=n_tool_calls,
        n_failed_tool_calls=n_failed,
        tool_failure_rate=tool_failure_rate,
        unique_tools_used=unique_tools,
        n_unique_tools=len(unique_tools),
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        total_latency_ms=total_latency_ms,
        workflow_complete=workflow_complete,
    )
