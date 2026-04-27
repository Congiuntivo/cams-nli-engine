from dataclasses import dataclass

from nli_engine.engine.workflow.base import Workflow, WorkflowContext
from nli_engine.engine.workflow.workflows.dummy import (
    DummyWorkflow,
    DummyWorkflowContext,
)
from nli_engine.engine.workflow.workflows.dummy_llm import (
    DummyLLMWorkflow,
    DummyLLMWorkflowContext,
)


@dataclass(frozen=True)
class WorkflowSpec:
    id: str
    name: str
    description: str
    workflow_class: type[Workflow]
    context_class: type[WorkflowContext]


WORKFLOW_REGISTRY: dict[str, WorkflowSpec] = {
    "dummy": WorkflowSpec(
        id="dummy",
        name="Dummy Setup",
        description="Adds a smartphone, CAWS endpoint, and participant role; returns serialized protocol.",
        workflow_class=DummyWorkflow,
        context_class=DummyWorkflowContext,
    ),
    "dummy_llm": WorkflowSpec(
        id="dummy_llm",
        name="Dummy LLM Setup",
        description="Uses an LLM to add a smartphone, CAWS endpoint, and participant role via tool calls.",
        workflow_class=DummyLLMWorkflow,
        context_class=DummyLLMWorkflowContext,
    ),
}
