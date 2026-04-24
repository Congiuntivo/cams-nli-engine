from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.registry import WorkflowSpec
from nli_engine.engine.workflow.result import TurnResult


class Conversation:
    def __init__(
        self,
        spec: WorkflowSpec,
        config: WorkflowConfig,
        session: ProtocolSession,
    ) -> None:
        self._workflow = spec.workflow_class(config, session)
        self._context = spec.context_class()

    def turn(self, user_input: str) -> TurnResult:
        return self._workflow.run_turn(user_input, self._context)
