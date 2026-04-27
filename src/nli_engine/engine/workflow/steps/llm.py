from __future__ import annotations

import json
import logging
import time
from typing import Any

from nli_engine.engine.llm.client import LLMClient
from nli_engine.engine.llm.dispatch import call_tool
from nli_engine.engine.llm.schema import bound_tool_to_schema
from nli_engine.engine.tools import BoundTool
from nli_engine.engine.workflow.base import Message, Step, WorkflowContext
from nli_engine.engine.workflow.log import StepLog

_log = logging.getLogger("nli_engine.llm")


def _message_to_dict(msg: Message) -> dict[str, Any]:
    d: dict[str, Any] = {"role": msg.role, "content": msg.content}
    if msg.tool_calls is not None:
        d["tool_calls"] = msg.tool_calls
    if msg.tool_call_id is not None:
        d["tool_call_id"] = msg.tool_call_id
    return d


def _dict_to_message(d: dict[str, Any]) -> Message:
    return Message(
        role=d["role"],
        content=d.get("content"),
        tool_calls=d.get("tool_calls"),
        tool_call_id=d.get("tool_call_id"),
    )


class LLMStep(Step):
    def __init__(
        self,
        name: str,
        tool_names: list[str],
        client: LLMClient,
        system_prompt: str,
        max_iterations: int = 10,
    ) -> None:
        super().__init__(name, tool_names)
        self._client = client
        self._system_prompt = system_prompt
        self._max_iterations = max_iterations

    def _build_messages(self, context: WorkflowContext) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt}
        ]
        messages.extend(_message_to_dict(m) for m in context.history)
        return messages

    def _build_tool_calls_payload(self, response: Any) -> list[dict[str, Any]]:
        return [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.name,
                    "arguments": json.dumps(tc.arguments),
                },
            }
            for tc in response.tool_calls
        ]

    def _execute_tool_calls(
        self,
        tool_calls: list[Any],
        tool_map: dict[str, BoundTool],
        new_messages: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        executed = []
        for tc in tool_calls:
            result = call_tool(tool_map[tc.name], tc.arguments)
            new_messages.append(
                {"role": "tool", "tool_call_id": tc.id, "content": result}
            )
            executed.append(
                {"name": tc.name, "arguments": tc.arguments, "result": result}
            )
            _log.info(
                "tool_call",
                extra={"event": "tool_call", "tool_name": tc.name},
            )
        return executed

    def _append_to_history(
        self, context: WorkflowContext, new_messages: list[dict[str, Any]]
    ) -> None:
        for d in new_messages:
            context.history.append(_dict_to_message(d))

    def run(
        self, context: WorkflowContext, tools: list[BoundTool]
    ) -> tuple[str, StepLog]:
        tool_schemas = [bound_tool_to_schema(t) for t in tools]
        tool_map = {t.name: t for t in tools}

        messages = self._build_messages(context)

        new_messages: list[dict[str, Any]] = []
        total_input = 0
        total_output = 0
        final_text = ""

        start = time.monotonic()

        for _ in range(self._max_iterations):
            all_messages = messages + new_messages
            _log.info(
                "llm_call",
                extra={"event": "llm_call", "model": self._client.model},
            )
            _log.debug(
                "llm_request",
                extra={
                    "event": "llm_request",
                    "model": self._client.model,
                    "messages": all_messages,
                    "n_tools": len(tool_schemas),
                },
            )

            response = self._client.complete(all_messages, tool_schemas)
            total_input += response.input_tokens
            total_output += response.output_tokens

            if response.tool_calls:
                tool_calls_raw = self._build_tool_calls_payload(response)
                new_messages.append(
                    {
                        "role": "assistant",
                        "content": response.text,
                        "tool_calls": tool_calls_raw,
                    }
                )
                executed = self._execute_tool_calls(
                    response.tool_calls, tool_map, new_messages
                )
                _log.debug(
                    "llm_tool_round",
                    extra={"event": "llm_tool_round", "tool_calls": executed},
                )
            else:
                final_text = response.text or ""
                new_messages.append({"role": "assistant", "content": final_text})
                _log.debug(
                    "llm_text_response",
                    extra={"event": "llm_text_response", "text": final_text},
                )
                _log.info(
                    "text_response",
                    extra={"event": "text_response", "text": final_text},
                )
                break
        else:
            final_text = "Reached maximum tool-call iterations without completing."
            new_messages.append({"role": "assistant", "content": final_text})

        self._append_to_history(context, new_messages)

        latency_ms = (time.monotonic() - start) * 1000
        log = StepLog(
            step_name=self.name,
            model=self._client.model,
            input_tokens=total_input,
            output_tokens=total_output,
            latency_ms=latency_ms,
        )
        return final_text, log
