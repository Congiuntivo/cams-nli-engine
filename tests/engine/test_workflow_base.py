from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from nli_engine.engine.workflow.base import (
    Message,
    Step,
    Workflow,
    WorkflowContext,
)
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.log import StepLog


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class ConcreteContext(WorkflowContext):
    pass


class ContextWithExtras(WorkflowContext):
    retrieved_chunks: list[str] = []


class ConcreteStep(Step):
    def run(self, context: WorkflowContext, tools: list[Any]) -> tuple[str, StepLog]:
        log = StepLog(
            step_name=self.name,
            model=None,
            input_tokens=0,
            output_tokens=0,
            latency_ms=0.0,
        )
        return ("done", log)


class ConcreteWorkflow(Workflow[ConcreteContext]):
    def run_turn(
        self, user_input: str, context: ConcreteContext
    ) -> tuple[str, list[StepLog]]:
        return (user_input, [])


def _make_session(*tool_names: str) -> MagicMock:
    tools = [MagicMock(name=n) for n in tool_names]
    for tool, name in zip(tools, tool_names):
        tool.name = name
    session = MagicMock()
    session.tools.return_value = tools
    return session


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------


def test_message_accepts_valid_roles() -> None:
    for role in ("user", "assistant", "tool"):
        msg = Message(role=role, content="hello")
        assert msg.role == role


def test_message_rejects_invalid_role() -> None:
    with pytest.raises(ValidationError):
        Message(role="system", content="hello")  # type: ignore[arg-type]


def test_message_accepts_string_content() -> None:
    msg = Message(role="user", content="hello")
    assert msg.content == "hello"


def test_message_accepts_list_content() -> None:
    msg = Message(role="assistant", content=[{"type": "text", "text": "hi"}])
    assert isinstance(msg.content, list)


# ---------------------------------------------------------------------------
# WorkflowContext
# ---------------------------------------------------------------------------


def test_workflow_context_direct_instantiation_raises() -> None:
    with pytest.raises(TypeError, match="abstract"):
        WorkflowContext(history=[])


def test_concrete_context_instantiates_empty() -> None:
    ctx = ConcreteContext()
    assert ctx.history == []


def test_concrete_context_carries_history() -> None:
    msg = Message(role="user", content="hi")
    ctx = ConcreteContext(history=[msg])
    assert len(ctx.history) == 1
    assert ctx.history[0].role == "user"


def test_context_with_extra_fields() -> None:
    ctx = ContextWithExtras(retrieved_chunks=["chunk1", "chunk2"])
    assert ctx.retrieved_chunks == ["chunk1", "chunk2"]
    assert ctx.history == []


# ---------------------------------------------------------------------------
# Step
# ---------------------------------------------------------------------------


def test_step_without_run_raises_on_instantiation() -> None:
    class IncompleteStep(Step):
        pass

    with pytest.raises(TypeError):
        IncompleteStep(name="incomplete", tool_names=[])  # type: ignore[abstract]


def test_concrete_step_instantiates() -> None:
    step = ConcreteStep(name="my_step", tool_names=["tool_a"])
    assert step.name == "my_step"
    assert step.tool_names == ["tool_a"]


def test_concrete_step_run_returns_log() -> None:
    step = ConcreteStep(name="s", tool_names=[])
    ctx = ConcreteContext()
    output, log = step.run(ctx, [])
    assert output == "done"
    assert log.step_name == "s"


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------


def test_workflow_builds_all_tools_from_session() -> None:
    session = _make_session("tool_a", "tool_b")
    wf = ConcreteWorkflow(config=WorkflowConfig(), session=session)
    assert set(wf._all_tools.keys()) == {"tool_a", "tool_b"}


def test_resolve_tools_returns_requested_subset() -> None:
    session = _make_session("tool_a", "tool_b", "tool_c")
    wf = ConcreteWorkflow(config=WorkflowConfig(), session=session)
    step = ConcreteStep(name="s", tool_names=["tool_a", "tool_c"])
    resolved = wf._resolve_tools(step)
    assert [t.name for t in resolved] == ["tool_a", "tool_c"]


def test_resolve_tools_empty_list_returns_empty() -> None:
    session = _make_session("tool_a")
    wf = ConcreteWorkflow(config=WorkflowConfig(), session=session)
    step = ConcreteStep(name="s", tool_names=[])
    assert wf._resolve_tools(step) == []


def test_resolve_tools_raises_on_unknown_tool() -> None:
    session = _make_session("tool_a")
    wf = ConcreteWorkflow(config=WorkflowConfig(), session=session)
    step = ConcreteStep(name="s", tool_names=["tool_a", "tool_x"])
    with pytest.raises(ValueError, match="tool_x"):
        wf._resolve_tools(step)
