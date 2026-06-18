from __future__ import annotations

from pydantic import BaseModel, Field


class AssemblyUnit(BaseModel):
    """One task-control assembly unit extracted from the planner's output.

    Attributes:
        name: Short label for the unit, matching the planner's numbering.
        description: Full natural-language description passed verbatim to the
            orchestrator as its per-unit instruction.
        needs_connected_device: True when the unit requires a connected device
            or service (e.g. LocationService, eSense). False when it uses only
            the primary device.
    """

    name: str
    description: str = Field(
        description=(
            "Full natural-language description of the assembly unit, including "
            "device, trigger, task, and any names or parameters the orchestrator needs."
        )
    )
    needs_connected_device: bool = Field(
        description=(
            "True if the unit requires a connected device or service "
            "(e.g. LocationService, WeatherService, eSense, Polar). "
            "False if it uses only a primary device (Smartphone, WebBrowser) or no device."
        )
    )


class AssemblyPlan(BaseModel):
    """The full set of assembly units extracted from the planner's output.

    Attributes:
        units: Ordered list of assembly units, one per task control in the plan.
    """

    units: list[AssemblyUnit]


class OrchestratorResult(BaseModel):
    """Classification of one orchestrator invocation's summary text.

    Attributes:
        success: True when all required specialists completed and the task control
            was bound. False when any component is missing or any specialist failed.
        open_questions: Unresolved issues or missing components blocking completion.
            Empty when success is True.
    """

    success: bool = Field(
        description=(
            "True if the assembly unit is complete: all required specialists ran "
            "and the task control was successfully bound. False if any specialist "
            "failed or any required component is missing."
        )
    )
    open_questions: list[str] = Field(
        default_factory=list,
        description="Unresolved issues or missing components reported by the orchestrator.",
    )
