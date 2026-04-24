from dataclasses import dataclass

from nli_engine.engine.workflow.base import Workflow, WorkflowContext
from nli_engine.engine.workflow.workflows.dummy import (
    DummyWorkflow,
    DummyWorkflowContext,
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
}
