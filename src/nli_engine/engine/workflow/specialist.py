from __future__ import annotations

from pydantic import BaseModel, Field

from nli_engine.engine.tools import BoundTool
from nli_engine.engine.workflow.base import Message, Step, WorkflowContext
from nli_engine.engine.workflow.log import StepLog


class SpecialistContext(WorkflowContext):
    """Isolated single-invocation context for a specialist step.

    Holds only the instruction passed by the Orchestrator; no main
    conversation history is visible to the specialist.
    """


class DelegationRequest(BaseModel):
    """Request model for Orchestrator-to-Specialist delegation calls.

    Attributes:
        instruction: Natural-language description of what to create or
            configure, including all names and parameters needed.
    """

    instruction: str = Field(
        description=(
            "Natural-language instruction for the specialist, including all "
            "names, types, and parameters needed to execute the task."
        )
    )


def build_specialist_tool(
    name: str,
    description: str,
    step: Step,
    domain_tools: list[BoundTool],
    log_sink: list[StepLog],
) -> BoundTool:
    """Wrap a specialist Step as a BoundTool callable by the Orchestrator.

    The returned tool accepts a DelegationRequest from the Orchestrator and
    runs the step in an isolated SpecialistContext that contains only the
    instruction. The specialist's final text response is returned as the
    tool result content.

    Args:
        name: Tool name exposed to the Orchestrator.
        description: When the Orchestrator should call this tool.
        step: Specialist Step to invoke on each delegation call.
        domain_tools: BoundTools available to the specialist during its run.
        log_sink: Mutable list the specialist's ``StepLog`` is appended to on
            each call. Lets the workflow surface specialist logs in
            ``TurnResult.logs`` instead of dropping them.

    Returns:
        BoundTool wrapping the specialist step with a DelegationRequest
        request model.
    """

    def _call(req: DelegationRequest) -> str:
        context = SpecialistContext()
        context.history.append(Message(role="user", content=req.instruction))
        text, log = step.run(context, domain_tools)
        log_sink.append(log)
        return text

    return BoundTool(
        name=name,
        description=description,
        request_model=DelegationRequest,
        call=_call,
    )
