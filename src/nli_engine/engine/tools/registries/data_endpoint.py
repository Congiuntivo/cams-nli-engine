from nli_engine.client._generated.authoring_client import (
    DataEndpointApi,
    DataEndpointRequest,
)
from nli_engine.engine.tools.spec import ToolSpec

DATA_ENDPOINT_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="add_data_endpoint",
        api_class=DataEndpointApi,
        method="add_data_endpoint",
        request_model=DataEndpointRequest,
        description="Configure a data upload endpoint (CAWS, SQLITE, or FILE).",
    ),
]
