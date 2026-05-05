from __future__ import annotations

from pathlib import Path

from nli_engine.engine.llm import LLMClient
from nli_engine.engine.prompts import load_prompt
from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.workflow.base import Message, Workflow, WorkflowContext
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.result import TurnResult
from nli_engine.engine.workflow.steps.llm import LLMStep


def _load_prompt(filename: Path) -> str:
    return load_prompt("nli_engine.engine.prompts", str(filename))


class DummyLLMWorkflowContext(WorkflowContext):
    """Workflow context for DummyLLMWorkflow."""


class DummyLLMWorkflow(Workflow[DummyLLMWorkflowContext]):
    """LLM-driven workflow that validates tool-calling by instructing the model
    to add a smartphone, CAWS endpoint, and participant role autonomously.

    Reads ``models["planner"]`` from WorkflowConfig and optionally
    ``parameters["api_base"]`` for non-default provider endpoints (e.g. Ollama).
    """

    def __init__(self, config: WorkflowConfig, session: ProtocolSession) -> None:
        """
        Args:
            config: Must contain ``models["planner"]``; may contain
                ``parameters["api_base"]`` for custom provider endpoints.
            session: Live authoring session used to bind and dispatch tools.

        Raises:
            KeyError: If ``config.models["planner"]`` is not set.
        """
        super().__init__(config, session)
        model = config.models["planner"]
        api_base: str | None = config.parameters.get("api_base")
        client = LLMClient(model=model, api_base=api_base)
        system_prompt = _load_prompt("dummy_llm_setup.md")
        self._step = LLMStep(
            name="dummy_llm_setup",
            tool_names=[
                "add_primary_smartphone",
                "add_data_endpoint",
                "add_participant_role",
            ],
            client=client,
            system_prompt=system_prompt,
        )

    def run_turn(self, user_input: str, context: DummyLLMWorkflowContext) -> TurnResult:
        """Append the user message, run the LLM step, and serialise the protocol.

        Args:
            user_input: Free-text instruction from the user.
            context: Mutable workflow state; the user message is appended before
                the step runs.

        Returns:
            TurnResult with ``done=True``, the LLM's text response, and the
            serialised protocol dict.
        """
        context.history.append(Message(role="user", content=user_input))
        tools = self._resolve_tools(self._step)
        text, log = self._step.run(context, tools)
        protocol = self._session.serialize()
        return TurnResult(message=text, logs=[log], done=True, protocol=protocol)
