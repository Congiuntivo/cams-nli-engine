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
from nli_engine.engine.workflow.workflows.one_shot_llm import (
    OneShotLLMWorkflow,
    OneShotLLMWorkflowContext,
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
    "one_shot_llm": WorkflowSpec(
        id="one_shot_llm",
        name="One-Shot LLM Setup",
        description=(
            "Uses one LLM step to refine the user instruction and a second to execute it, "
            "validating tool calls by instructing the model to add a smartphone, CAWS endpoint, "
            "and participant role autonomously."
        ),
        workflow_class=OneShotLLMWorkflow,
        context_class=OneShotLLMWorkflowContext,
    ),
}
