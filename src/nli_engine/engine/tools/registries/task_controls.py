from nli_engine.client._generated.authoring_client import (
    TaskControlRequest,
    TaskControlsApi,
)
from nli_engine.engine.tools.spec import ToolSpec

TASK_CONTROLS_MUTATION_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="add_task_control",
        api_class=TaskControlsApi,
        method="add_task_control",
        description="Bind a task to a trigger on a specific device role.",
        request_model=TaskControlRequest,
    ),
]

TASK_CONTROLS_READ_ONLY_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="get_task_controls",
        api_class=TaskControlsApi,
        method="get_task_controls",
        description="Return all task-trigger bindings added so far.",
    ),
]
