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
    return load_prompt("nli_engine.engine.prompts.one_shot", str(filename))


class OneShotLLMWorkflowContext(WorkflowContext):
    """Workflow context for OneShotLLMWorkflow."""


class OneShotLLMWorkflow(Workflow[OneShotLLMWorkflowContext]):
    """Three-step LLM workflow: refiner → planner → executor.

    The refiner rewrites the raw user message into a clean, unambiguous natural
    language description. The planner reads that description and produces a
    concise ordered action plan. The executor follows the plan and calls the
    authoring API tools to build the protocol.

    Reads ``models["refiner"]``, ``models["planner"]``, and
    ``models["executor"]`` from WorkflowConfig, and optionally
    ``parameters["api_base"]`` for non-default provider endpoints.
    """

    def __init__(self, config: WorkflowConfig, session: ProtocolSession) -> None:
        """
        Args:
            config: Must contain ``models["refiner"]``, ``models["planner"]``,
                and ``models["executor"]``; may contain ``parameters["api_base"]``
                for custom provider endpoints.
            session: Live authoring session used to bind and dispatch tools.

        Raises:
            KeyError: If any required model key is absent from ``config.models``.
        """
        super().__init__(config, session)
        api_base: str | None = config.parameters.get("api_base")

        planner_client = LLMClient(model=config.models["planner"], api_base=api_base)
        self._planning_step = LLMStep(
            name="planner",
            client=planner_client,
            system_prompt=_load_prompt("planner.md"),
            max_iterations=config.max_iterations.get("planner", 1),
        )

        refiner_client = LLMClient(model=config.models["refiner"], api_base=api_base)
        self._refinement_step = LLMStep(
            name="refiner",
            client=refiner_client,
            system_prompt=_load_prompt("refiner.md"),
            max_iterations=config.max_iterations.get("refiner", 3),
        )

        executor_client = LLMClient(model=config.models["executor"], api_base=api_base)
        self._execution_step = LLMStep(
            name="executor",
            tool_names=list(self._all_tools),
            client=executor_client,
            system_prompt=_load_prompt("executor.md"),
            max_iterations=config.max_iterations.get("executor", 10),
        )

    def run_turn(
        self, user_input: str, context: OneShotLLMWorkflowContext
    ) -> TurnResult:
        """Run one user turn through the full refiner → planner → executor pipeline.

        The user message is appended to the shared history before any step runs.
        Each step extends that history so the next step has full context.

        Args:
            user_input: Raw free-text instruction from the user.
            context: Mutable workflow state shared across all three steps.

        Returns:
            TurnResult with ``done=True``, the executor's text response, and the
            serialised protocol dict.
        """
        context.history.append(Message(role="user", content=user_input))

        logs = []

        _, log = self._refinement_step.run(context)
        logs.append(log)

        _, log = self._planning_step.run(context)
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
