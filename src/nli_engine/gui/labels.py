"""Mapping from workflow step names to user-facing status labels."""

from __future__ import annotations

STATUS_LABELS: dict[str, str] = {
    "refiner": "Refining your input...",
    "planner": "Formulating a plan...",
    "extractor": "Extracting the assembly plan...",
    "setup_specialist": "Setting up the protocol...",
    "orchestrator": "Assembling the protocol...",
    "orchestrator_result": "Verifying the assembly...",
    "device_specialist": "Configuring a device...",
    "trigger_specialist": "Setting up a trigger...",
    "task_specialist": "Defining a task...",
    "task_control_assembler": "Wiring a task control...",
    "explainer": "Writing the explanation...",
}


def friendly(step_name: str) -> str:
    """Return the friendly status label for a step, falling back to the raw name."""
    return STATUS_LABELS.get(step_name, step_name)
