from __future__ import annotations

import importlib.resources

from nli_engine.engine.llm import LLMClient
from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.workflow.base import Message, Workflow, WorkflowContext
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.result import TurnResult
from nli_engine.engine.workflow.steps.llm import LLMStep


def _load_prompt(filename: str) -> str:
    ref = importlib.resources.files("nli_engine.engine.prompts") / filename
    return ref.read_text(encoding="utf-8")


class DummyLLMWorkflowContext(WorkflowContext):
    pass


class DummyLLMWorkflow(Workflow[DummyLLMWorkflowContext]):
    def __init__(self, config: WorkflowConfig, session: ProtocolSession) -> None:
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
        context.history.append(Message(role="user", content=user_input))
        tools = self._resolve_tools(self._step)
        text, log = self._step.run(context, tools)
        protocol = self._session.serialize()
        return TurnResult(message=text, logs=[log], done=True, protocol=protocol)
