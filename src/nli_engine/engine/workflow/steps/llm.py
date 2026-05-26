from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from nli_engine.engine.llm.client import LLMClient, LLMResponse, ToolCall
from nli_engine.engine.llm.dispatch import call_tool
from nli_engine.engine.llm.schema import bound_tool_to_schema
from nli_engine.engine.retrieval.chunk import RetrievedChunk
from nli_engine.engine.retrieval.query import LastUserMessageExtractor, QueryExtractor
from nli_engine.engine.retrieval.retriever import Retriever
from nli_engine.engine.tools import BoundTool
from nli_engine.engine.workflow.base import Message, Step, WorkflowContext
from nli_engine.engine.workflow.log import StepLog

_log = logging.getLogger("nli_engine.llm")


def _format_chunks(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks as a source-annotated block for prompt injection."""
    return (
        "<context>"
        + "\n"
        + "\n".join(
            f'<document source="{c.source}">\n{c.content}</document>' for c in chunks
        )
        + "\n"
        + "</context>"
    )  # Anthropic's recommended format for retrieval-augmented generation.


class LLMStep(Step):
    """Workflow step that runs an agentic LLM loop until the model stops calling tools.

    On each ``run()`` call the step sends the conversation history to the LLM,
    dispatches any tool calls, feeds results back, and repeats until the model
    produces a plain text response or ``max_iterations`` is reached.

    When ``retriever`` is provided the step runs retrieval before each LLM call,
    formats the results, and makes them available as ``{{var: retrieved_context}}``
    in the system prompt. Retrieval is entirely local to the step — no shared
    context state is read or written.
    """

    def __init__(
        self,
        name: str,
        client: LLMClient,
        system_prompt: str,
        tool_names: list[str] = [],
        max_iterations: int = 10,
        retriever: Retriever | None = None,
        query_extractor: QueryExtractor | None = None,
        top_k: int = 5,
    ) -> None:
        """
        Args:
            name: Step name; appears in StepLog.
            client: Configured LLM transport.
            system_prompt: System message prepended before the conversation history
                on every LLM call.
            tool_names: Names of the BoundTools this step may call.
            max_iterations: Maximum number of tool-call rounds before aborting
                with an error message.
            retriever: Optional retrieval backend. When set, retrieval runs before
                each LLM call and its output is injected via ``{{var: retrieved_context}}``.
            query_extractor: Strategy for deriving the retrieval query from context.
                Defaults to ``LastUserMessageExtractor`` when ``None``.
            top_k: Maximum number of chunks to retrieve. Ignored when ``retriever``
                is ``None``.
        """
        super().__init__(name, tool_names)
        self._client = client
        self._system_prompt = system_prompt
        self._max_iterations = max_iterations
        self._retriever = retriever
        self._query_extractor: QueryExtractor = (
            query_extractor
            if query_extractor is not None
            else LastUserMessageExtractor()
        )
        self._top_k = top_k

    def _render_system_prompt(
        self, context: WorkflowContext, extra_variables: dict[str, str] = {}
    ) -> str:
        """Render ``{{var: name}}`` tags in the system prompt from context variables.

        Args:
            context: Workflow context whose ``context_variables()`` supplies values.
            extra_variables: Additional variables merged on top of the context's own
                variables. These take precedence on collision.

        Returns:
            System prompt with all ``{{var: name}}`` tags replaced.

        Raises:
            ValueError: If the prompt references a variable not returned by the context.
        """
        variables = {**context.context_variables(), **extra_variables}

        def _replace(match: re.Match) -> str:
            name = match.group(1)
            if name not in variables:
                raise ValueError(
                    f"System prompt of step '{self.name}' references "
                    f"undefined variable '{{{{var: {name}}}}}'."
                )
            return variables[name]

        return re.sub(r"\{\{var:\s*(\w+)\s*\}\}", _replace, self._system_prompt)

    def _build_messages(
        self, context: WorkflowContext, extra_variables: dict[str, str] = {}
    ) -> list[dict[str, Any]]:
        """Construct the messages list for the LLM: rendered system prompt + conversation history."""
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": self._render_system_prompt(context, extra_variables),
            }
        ]
        messages.extend(m.to_dict() for m in context.history)
        return messages

    def _build_tool_context(
        self, tools: list[BoundTool]
    ) -> tuple[list[dict[str, Any]], dict[str, BoundTool]]:
        """Return tool schemas for the LLM and a name→tool map for dispatch."""
        schemas = [bound_tool_to_schema(t) for t in tools]
        tool_map = {t.name: t for t in tools}
        return schemas, tool_map

    def _log_request(
        self, messages: list[dict[str, Any]], tool_schemas: list[dict[str, Any]]
    ) -> None:
        """Emit INFO and DEBUG log records for an outgoing LLM request."""
        _log.info("llm_call", extra={"event": "llm_call", "model": self._client.model})
        _log.debug(
            "llm_request",
            extra={
                "event": "llm_request",
                "model": self._client.model,
                "messages": messages,
                "n_tools": len(tool_schemas),
            },
        )

    def _handle_tool_response(
        self,
        response: LLMResponse,
        tool_map: dict[str, BoundTool],
        new_messages: list[dict[str, Any]],
    ) -> None:
        """Append the assistant tool-call message, execute tools, and log the round."""
        tool_calls_raw = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.name, "arguments": json.dumps(tc.arguments)},
            }
            for tc in response.tool_calls
        ]
        new_messages.append(
            {
                "role": "assistant",
                "content": response.text,
                "tool_calls": tool_calls_raw,
            }
        )
        executed = self._execute_tool_calls(response.tool_calls, tool_map, new_messages)
        _log.debug(
            "llm_tool_round",
            extra={"event": "llm_tool_round", "tool_calls": executed},
        )

    def _handle_text_response(
        self,
        response: LLMResponse,
        new_messages: list[dict[str, Any]],
    ) -> str:
        """Append the final assistant message, log it, and return the text."""
        final_text = response.text or ""
        new_messages.append({"role": "assistant", "content": final_text})
        _log.debug(
            "llm_text_response",
            extra={"event": "llm_text_response", "text": final_text},
        )
        _log.info("text_response", extra={"event": "text_response", "text": final_text})
        return final_text

    def _execute_tool_calls(
        self,
        tool_calls: list[ToolCall],
        tool_map: dict[str, BoundTool],
        new_messages: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        executed = []
        for i, tc in enumerate(tool_calls):
            result = call_tool(tool_map[tc.name], tc.arguments)
            if result.is_error and not result.retryable:
                raise RuntimeError(result.content)
            new_messages.append(
                {"role": "tool", "tool_call_id": tc.id, "content": result.content}
            )
            executed.append(
                {
                    "name": tc.name,
                    "arguments": tc.arguments,
                    "result": result.content,
                    "is_error": result.is_error,
                }
            )
            _log.info(
                "tool_call",
                extra={
                    "event": "tool_call",
                    "tool_name": tc.name,
                    "is_error": result.is_error,
                },
            )
            if result.is_error:
                # The API requires every tool_call_id in the assistant message to
                # have a corresponding tool result. Append placeholder responses for
                # any calls that won't be executed so the message sequence stays valid.
                for skipped in tool_calls[i + 1 :]:
                    new_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": skipped.id,
                            "content": "Skipped: a preceding tool call in this batch failed.",
                        }
                    )
                break
        return executed

    def _append_to_history(
        self, context: WorkflowContext, new_messages: list[dict[str, Any]]
    ) -> None:
        """Append all the new messages from this step's run to the context history for future turns."""
        for d in new_messages:
            context.history.append(Message.from_dict(d))

    def _run(
        self, context: WorkflowContext, tools: list[BoundTool] = []
    ) -> tuple[str, StepLog]:
        """Run the loop and return the final text response and log entry.

        Appends all intermediate messages (assistant tool-call turns and tool
        results) to ``context.history`` before returning so future turns carry
        full context.

        Args:
            context: Shared workflow state; history is read and extended in place.
            tools: BoundTools this step may invoke during the loop.

        Returns:
            A tuple of ``(final text response, StepLog)`` with aggregated
            token counts across all iterations.
        """
        tool_schemas, tool_map = self._build_tool_context(tools)

        extra_vars: dict[str, str] = {"retrieved_context": ""}
        retrieval_extra: dict[str, Any] = {}
        if self._retriever is not None:
            query = self._query_extractor.extract(context)
            chunks = self._retriever.retrieve(query, self._top_k)
            extra_vars["retrieved_context"] = _format_chunks(chunks) if chunks else ""
            retrieval_extra = {"query": query, "n_chunks": len(chunks)}

        messages = self._build_messages(context, extra_vars)

        # Iteration variables
        new_messages: list[dict[str, Any]] = []
        total_input, total_output = 0, 0
        final_text = ""
        start = time.monotonic()

        # Tool loop: call the LLM, dispatch any tool calls, then repeat.
        #   - The loop exits as soon as the model returns a plain text response.
        for _ in range(self._max_iterations):
            self._log_request(messages + new_messages, tool_schemas)

            response = self._client.complete(messages + new_messages, tool_schemas)
            total_input += response.input_tokens
            total_output += response.output_tokens

            if response.tool_calls:
                self._handle_tool_response(response, tool_map, new_messages)
            else:
                final_text = self._handle_text_response(response, new_messages)
                break
        else:
            # Safety valve: model kept calling tools past the iteration limit.
            final_text = "Reached maximum tool-call iterations without completing."
            new_messages.append({"role": "assistant", "content": final_text})

        # Persist the full exchange to context so future turns have complete history.
        self._append_to_history(context, new_messages)

        return final_text, StepLog(
            step_name=self.name,
            model=self._client.model,
            input_tokens=total_input,
            output_tokens=total_output,
            latency_ms=(time.monotonic() - start) * 1000,
            extra=retrieval_extra,
        )
