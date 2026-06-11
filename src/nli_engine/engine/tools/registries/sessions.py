from nli_engine.client._generated.authoring_client import (
    SessionsApi,
    SetApplicationDataRequest,
)
from nli_engine.engine.tools.spec import ToolSpec

SESSIONS_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="set_application_data",
        api_class=SessionsApi,
        method="set_application_data",
        request_model=SetApplicationDataRequest,
        description="Store free-form key/value application data on the study protocol.",
    ),
]
