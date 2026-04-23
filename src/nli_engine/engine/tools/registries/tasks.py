from nli_engine.client._generated.authoring_client import (
    AppTaskRequest,
    BackgroundTaskRequest,
    HealthAppTaskRequest,
    TasksApi,
    WebTaskRequest,
)
from nli_engine.engine.tools.spec import ToolSpec

TASKS_MUTATION_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="add_background_task",
        api_class=TasksApi,
        method="add_background_task",
        request_model=BackgroundTaskRequest,
        description="Add a passive background data-collection task.",
    ),
    ToolSpec(
        name="add_app_task",
        api_class=TasksApi,
        method="add_app_task",
        request_model=AppTaskRequest,
        description="Add an active app-based task (survey, cognitive test, etc.).",
    ),
    ToolSpec(
        name="add_health_app_task",
        api_class=TasksApi,
        method="add_health_app_task",
        request_model=HealthAppTaskRequest,
        description="Add a health app task (step count, heart rate, etc.).",
    ),
    ToolSpec(
        name="add_web_task",
        api_class=TasksApi,
        method="add_web_task",
        request_model=WebTaskRequest,
        description="Add a web-based task with a URL.",
    ),
]

TASKS_READ_ONLY_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="get_tasks",
        api_class=TasksApi,
        method="get_tasks",
        description="Return all tasks added so far.",
    ),
]
