from __future__ import annotations

import logging
from typing import Protocol

from nli_engine.engine.llm.client import LLMClient
from nli_engine.engine.workflow.base import WorkflowContext

_log = logging.getLogger("nli_engine.retrieval")


class QueryExtractor(Protocol):
    """Interface for deriving a retrieval query from the current workflow context.

    The Protocol allows both trivial implementations (e.g. returning the last
    user message) and LLM-based implementations (e.g. generating a focused
    sub-query) to satisfy the same interface without sharing a base class.
    """

    def extract(self, context: WorkflowContext) -> str:
        """Derive a retrieval query from the current context.

        Args:
            context: The workflow context at the moment retrieval is triggered.

        Returns:
            A string query suitable for passing to a ``Retriever``.
        """
        ...


class LastUserMessageExtractor:
    """Extracts the most recent user message from context history as the retrieval query."""

    def extract(self, context: WorkflowContext) -> str:
        """Return the content of the last user message, or an empty string if none exists.

        Args:
            context: The workflow context whose history is searched.

        Returns:
            Content of the last user-role message, or ``""`` if history is empty.
        """
        user_messages = [m for m in context.history if m.role == "user"]
        if not user_messages:
            return ""
        return user_messages[-1].content or ""


class LLMQueryRewriter:
    """LLM-backed query extractor that rewrites the current context into a focused retrieval query.

    The rewriter sends the system prompt plus the natural-language portion of
    the conversation history to a small/cheap LLM and returns the model's text
    response as the retrieval query. Tool-call and tool-result turns are
    stripped so the request stays valid when sent without a ``tools`` argument.

    On any failure (empty response, exception, blank query), falls back to the
    last user message to keep retrieval functional.
    """

    def __init__(self, client: LLMClient, system_prompt: str) -> None:
        """
        Args:
            client: LLM transport configured with a small/cheap model.
            system_prompt: Instruction telling the model to output one focused
                retrieval query as plain text.
        """
        self._client = client
        self._system_prompt = system_prompt
        self._fallback = LastUserMessageExtractor()

    def extract(self, context: WorkflowContext) -> str:
        """Generate a focused retrieval query from the conversation context.

        Args:
            context: The workflow context whose history is rewritten.

        Returns:
            A short query string. Falls back to the last user message if the
            rewriter produces an empty response or raises.
        """
        nl_messages: list[dict] = []
        for m in context.history:
            # Skip tool-call assistant turns and tool-result turns: they
            # require a matching ``tools`` argument to be valid and add no
            # information the rewriter needs.
            if m.role == "tool" or m.tool_calls:
                continue
            nl_messages.append({"role": m.role, "content": m.content})

        if not nl_messages:
            return ""

        messages = [{"role": "system", "content": self._system_prompt}] + nl_messages

        try:
            response = self._client.complete(messages, tools=[])
        except Exception as exc:
            _log.warning(
                "query_rewriter_failed",
                extra={"event": "query_rewriter_failed", "error": str(exc)},
            )
            return self._fallback.extract(context)

        query = (response.text or "").strip()
        if not query:
            return self._fallback.extract(context)
        return query
