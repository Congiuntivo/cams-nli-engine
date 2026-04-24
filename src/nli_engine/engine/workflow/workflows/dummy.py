import json

from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.workflow.base import Workflow, WorkflowContext
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.log import StepLog
from nli_engine.engine.workflow.steps.dummy import DummySetupStep


class DummyWorkflowContext(WorkflowContext):
    pass


class DummyWorkflow(Workflow[DummyWorkflowContext]):
    def __init__(self, config: WorkflowConfig, session: ProtocolSession) -> None:
        super().__init__(config, session)
        self._step = DummySetupStep()

    def run_turn(
        self, user_input: str, context: DummyWorkflowContext
    ) -> tuple[str, list[StepLog]]:
        tools = self._resolve_tools(self._step)
        _, log = self._step.run(context, tools)
        protocol = self._session.serialize()
        return (json.dumps(protocol, indent=2), [log])
