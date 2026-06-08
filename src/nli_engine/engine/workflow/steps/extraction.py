from __future__ import annotations

import time
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from nli_engine.engine.llm.client import LLMClient
from nli_engine.engine.tools import BoundTool
from nli_engine.engine.workflow.base import Step, WorkflowContext
from nli_engine.engine.workflow.log import StepLog

T = TypeVar("T", bound=BaseModel)


class ExtractionStep(Step, Generic[T]):
    """Workflow step that extracts a structured Pydantic model from conversation history.

    Calls ``LLMClient.complete_structured`` with the current conversation history
    and a system prompt. Does not call tools and does not append any messages to
    ``context.history`` — the step is invisible to the rest of the conversation.
    """

    def __init__(
        self,
        name: str,
        client: LLMClient,
        system_prompt: str,
        schema: type[T],
    ) -> None:
        """
        Args:
            name: Step name; appears in StepLog.
            client: Configured LLM transport.
            system_prompt: Instruction for extracting the structured output.
            schema: Pydantic model class that defines the expected response shape.
        """
        super().__init__(name, tool_names=[])
        self._client = client
        self._system_prompt = system_prompt
        self._schema = schema

    def _run(
        self, context: WorkflowContext, tools: list[BoundTool] = []
    ) -> tuple[T, StepLog]:
        """Extract the structured model from the conversation and return it.

        Args:
            context: Shared workflow state; history is read but never modified.
            tools: Unused; present only to satisfy the Step interface.

        Returns:
            A tuple of ``(parsed model instance, StepLog)`` with token counts.
        """
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt}
        ]
        messages.extend(m.to_dict() for m in context.history)

        start = time.monotonic()
        response = self._client.complete_structured(messages, self._schema)

        return response.parsed, StepLog(
            step_name=self.name,
            model=self._client.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            latency_ms=(time.monotonic() - start) * 1000,
        )
