"""ReAct-style loop for the baseline agent."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from openai import AsyncOpenAI

from react_baseline.logger import SessionLogger
from react_baseline.mcp_bridge import McpBridge

_TERMINATION_TOOL = "serializeProtocol"


@dataclass
class AgentResult:
    """Outcome of one baseline cell run.

    Attributes:
        final_text: Last assistant message text (may be empty).
        serialized: Whether the agent ever received a successful
            ``serializeProtocol`` result.
        total_input_tokens: Prompt tokens consumed across all LLM calls.
        total_output_tokens: Completion tokens produced across all LLM calls.
        latency_ms: Wall-clock duration of the loop in milliseconds.
        n_llm_calls: Number of ``chat.completions.create`` calls made.
        turns_used: Number of ReAct iterations executed.
        hit_turn_cap: Whether the loop exited because of the turn cap.
    """

    final_text: str = ""
    serialized: bool = False
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    latency_ms: float = 0.0
    n_llm_calls: int = 0
    turns_used: int = 0
    hit_turn_cap: bool = False
    messages: list[dict[str, Any]] = field(default_factory=list)


async def run_cell(
    *,
    user_prompt: str,
    system_prompt: str,
    model: str,
    turn_cap: int,
    temperature: float,
    seed: int | None,
    bridge: McpBridge,
    logger: SessionLogger,
) -> AgentResult:
    """Run one ReAct cell end-to-end.

    Args:
        user_prompt: The verbatim natural-language prompt from the manifest.
        system_prompt: Rendered system prompt (already contains sessionId).
        model: OpenAI model name (e.g. ``"gpt-5.4"``).
        turn_cap: Maximum number of LLM rounds before aborting.
        temperature: Sampling temperature (0.0 for maximum determinism).
        seed: Optional OpenAI seed.
        bridge: Live :class:`McpBridge` with both MCP servers open.
        logger: :class:`SessionLogger` receiving the JSONL event stream.

    Returns:
        An :class:`AgentResult` summarising the run.
    """
    client = AsyncOpenAI()
    tools = bridge.openai_tools()

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    result = AgentResult()
    t0 = time.perf_counter()

    for turn in range(turn_cap):
        result.turns_used = turn + 1

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": temperature,
        }
        if seed is not None:
            kwargs["seed"] = seed

        logger.llm_call(model=model)
        response = await client.chat.completions.create(**kwargs)
        result.n_llm_calls += 1

        usage = response.usage
        if usage is not None:
            result.total_input_tokens += usage.prompt_tokens or 0
            result.total_output_tokens += usage.completion_tokens or 0

        message = response.choices[0].message
        tool_calls = message.tool_calls or []
        assistant_msg: dict[str, Any] = {
            "role": "assistant",
            "content": message.content or "",
        }
        if tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ]
        messages.append(assistant_msg)

        if not tool_calls:
            result.final_text = message.content or ""
            break

        round_summary: list[dict[str, Any]] = []
        for tc in tool_calls:
            name = tc.function.name
            try:
                arguments = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                arguments = {}

            tool_text, is_error = await bridge.call(name, arguments)
            logger.tool_call(tool_name=name, is_error=is_error)
            round_summary.append(
                {
                    "name": name,
                    "is_error": is_error,
                }
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_text,
                }
            )

            if name == _TERMINATION_TOOL and not is_error:
                result.serialized = True

        logger.llm_tool_round(tool_calls=round_summary)

        if result.serialized:
            break
    else:
        result.hit_turn_cap = True

    result.latency_ms = (time.perf_counter() - t0) * 1000.0
    result.messages = messages
    return result
