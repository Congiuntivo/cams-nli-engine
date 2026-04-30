from __future__ import annotations

import importlib.resources
from pathlib import Path

from nli_engine.engine.llm import LLMClient
from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.workflow.base import Message, Workflow, WorkflowContext
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.result import TurnResult
from nli_engine.engine.workflow.steps.llm import LLMStep


def _load_prompt(filename: Path) -> str:
    ref = importlib.resources.files("nli_engine.engine.prompts.one_shot") / filename
    return ref.read_text(encoding="utf-8")


class OneShotLLMWorkflowContext(WorkflowContext):
    """Workflow context for OneShotLLMWorkflow."""


class OneShotLLMWorkflow(Workflow[OneShotLLMWorkflowContext]):
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
        api_base: str | None = config.parameters.get("api_base")

        refiner_client = LLMClient(model=config.models["refiner"], api_base=api_base)
        refiner_system_prompt = _load_prompt("refiner.md")
        self._refinement_step = LLMStep(
            name="refiner",
            client=refiner_client,
            system_prompt=refiner_system_prompt,
        )

        executor_client = LLMClient(model=config.models["planner"], api_base=api_base)
        executort_system_prompt = _load_prompt("executor.md")
        executor_tool_names = list(self._all_tools)
        self._execution_step = LLMStep(
            name="executor",
            tool_names=executor_tool_names,
            client=executor_client,
            system_prompt=executort_system_prompt,
        )

    def run_turn(
        self, user_input: str, context: OneShotLLMWorkflowContext
    ) -> TurnResult:
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

        logs = []

        _, log = self._refinement_step.run(context)
        logs.append(log)

        text, log = self._execution_step.run(
            context,
            self._resolve_tools(self._execution_step),
        )
        logs.append(log)

        protocol = self._session.serialize()
        return TurnResult(
            message=text,
            logs=logs,
            done=True,
            protocol=protocol,
        )
