from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.tools import BoundTool
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.log import StepLog
from nli_engine.engine.workflow.result import TurnResult

_log = logging.getLogger("nli_engine.step")


class Message(BaseModel):
    """One message in LLM API format, compatible with the OpenAI chat protocol.

    Attributes:
        role: Speaker role — ``"user"``, ``"assistant"``, or ``"tool"``.
        content: Message text or multi-part content list. ``None`` for assistant
            turns that contain only tool calls.
        tool_calls: Raw tool call dicts in OpenAI format; set on assistant turns
            that include tool invocations, ``None`` otherwise.
        tool_call_id: Matches the originating ``ToolCall.id``; set on
            tool-result turns, ``None`` otherwise.
    """

    role: Literal["user", "assistant", "tool"]
    content: str | list[Any] | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.tool_calls is not None:
            d["tool_calls"] = self.tool_calls
        if self.tool_call_id is not None:
            d["tool_call_id"] = self.tool_call_id
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Message:
        return cls(
            role=d["role"],
            content=d.get("content"),
            tool_calls=d.get("tool_calls"),
            tool_call_id=d.get("tool_call_id"),
        )


class WorkflowContext(BaseModel, ABC):
    """Abstract mutable state shared across every step in a workflow turn.

    Subclass this for each concrete workflow and add the fields that steps need.
    The base carries only the conversation history.

    Attributes:
        history: Full conversation history including tool call exchanges,
            never truncated at this layer.
    """

    history: list[Message] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if type(self) is WorkflowContext:
            raise TypeError(
                "WorkflowContext is abstract and cannot be instantiated directly"
            )


C = TypeVar("C", bound=WorkflowContext)


class Step(ABC):
    """Abstract base for all workflow step types.

    Each step declares the tool names it may use and receives only that subset
    from the workflow. Non-LLM steps (retrieval, formatting, …) subclass Step
    directly; LLMStep is the standard LLM-calling specialisation.
    """

    def __init__(self, name: str, tool_names: list[str]) -> None:
        """
        Args:
            name: Unique step name within its workflow; appears in StepLog.
            tool_names: Names of BoundTools this step is permitted to call.
        """
        self.name = name
        self.tool_names = tool_names

    def run(
        self, context: WorkflowContext, tools: list[BoundTool] = []
    ) -> tuple[Any, StepLog]:
        """Execute the step, bookend it with trace logs, and return its output.

        Args:
            context: Shared workflow state; steps may read and mutate it.
            tools: The subset of BoundTools declared by this step.

        Returns:
            A tuple of ``(step output, StepLog)``. The output type is
            step-specific; LLMStep returns a ``str``.
        """
        _log.info("step_begin", extra={"event": "step_begin", "step_name": self.name})
        result = self._run(context, tools)
        _log.info("step_end", extra={"event": "step_end", "step_name": self.name})
        return result

    @abstractmethod
    def _run(
        self, context: WorkflowContext, tools: list[BoundTool]
    ) -> tuple[Any, StepLog]:
        """Implement the step logic and return its output alongside a log entry.

        Args:
            context: Shared workflow state; steps may read and mutate it.
            tools: The subset of BoundTools declared by this step.

        Returns:
            A tuple of ``(step output, StepLog)``. The output type is
            step-specific; LLMStep returns a ``str``.
        """
        ...


class Workflow(ABC, Generic[C]):
    """Abstract workflow base, generic over its WorkflowContext subclass C.

    A workflow orchestrates a sequence of Steps against a ProtocolSession and
    returns a TurnResult per user turn. The type parameter C lets each subclass
    declare its context type precisely so ``run_turn()`` is statically typed.
    """

    def __init__(self, config: WorkflowConfig, session: ProtocolSession) -> None:
        """
        Args:
            config: Workflow parameters including model identifiers.
            session: Live authoring session; its tools are pre-bound here.
        """
        self.config = config
        self._session = session
        self._all_tools: dict[str, BoundTool] = {t.name: t for t in session.tools()}

    @abstractmethod
    def run_turn(self, user_input: str, context: C) -> TurnResult:
        """Process one user turn and return the result.

        Args:
            user_input: Raw text from the user.
            context: Mutable workflow state persisted across turns.

        Returns:
            TurnResult with the response message, step logs, and completion flag.
        """
        ...

    def _resolve_tools(self, step: Step) -> list[BoundTool]:
        """Filter the session's tools to only those declared by the given step.

        Args:
            step: The step whose tool_names define the permitted subset.

        Returns:
            Ordered list of BoundTools matching the step's declared names.

        Raises:
            ValueError: If any declared tool name is absent from the session.
        """
        missing = [n for n in step.tool_names if n not in self._all_tools]
        if missing:
            raise ValueError(f"Step '{step.name}' declared unknown tools: {missing}")
        return [self._all_tools[n] for n in step.tool_names]
