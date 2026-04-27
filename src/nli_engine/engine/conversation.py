from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.registry import WorkflowSpec
from nli_engine.engine.workflow.result import TurnResult


class Conversation:
    """GUI-agnostic driver that holds a workflow and its context for one user session.

    Neither the CLI nor the GUI interacts with Workflow or WorkflowContext
    directly — they call ``turn()`` on this class.
    """

    def __init__(
        self,
        spec: WorkflowSpec,
        config: WorkflowConfig,
        session: ProtocolSession,
    ) -> None:
        """
        Args:
            spec: Workflow specification identifying which workflow and context
                classes to instantiate.
            config: Workflow parameters (model identifiers, provider settings, …).
            session: Live authoring session bound to the target server.
        """
        self._workflow = spec.workflow_class(config, session)
        self._context = spec.context_class()

    def turn(self, user_input: str) -> TurnResult:
        """Process one user turn and return the result.

        Args:
            user_input: Raw text from the user.

        Returns:
            TurnResult from the underlying workflow.
        """
        return self._workflow.run_turn(user_input, self._context)
