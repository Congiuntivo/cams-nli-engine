from __future__ import annotations

from typing import Protocol

from nli_engine.engine.workflow.base import WorkflowContext


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
