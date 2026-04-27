from abc import ABC, abstractmethod
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.tools import BoundTool
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.log import StepLog
from nli_engine.engine.workflow.result import TurnResult


class Message(BaseModel):
    role: Literal["user", "assistant", "tool"]
    content: str | list[Any] | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


class WorkflowContext(BaseModel, ABC):
    history: list[Message] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if type(self) is WorkflowContext:
            raise TypeError(
                "WorkflowContext is abstract and cannot be instantiated directly"
            )


C = TypeVar("C", bound=WorkflowContext)


class Step(ABC):
    def __init__(self, name: str, tool_names: list[str]) -> None:
        self.name = name
        self.tool_names = tool_names

    @abstractmethod
    def run(
        self, context: WorkflowContext, tools: list[BoundTool]
    ) -> tuple[Any, StepLog]: ...


class Workflow(ABC, Generic[C]):
    def __init__(self, config: WorkflowConfig, session: ProtocolSession) -> None:
        self.config = config
        self._session = session
        self._all_tools: dict[str, BoundTool] = {t.name: t for t in session.tools()}

    @abstractmethod
    def run_turn(self, user_input: str, context: C) -> TurnResult: ...

    def _resolve_tools(self, step: Step) -> list[BoundTool]:
        missing = [n for n in step.tool_names if n not in self._all_tools]
        if missing:
            raise ValueError(f"Step '{step.name}' declared unknown tools: {missing}")
        return [self._all_tools[n] for n in step.tool_names]
