from nli_engine.client._generated.authoring_client import (
    PrimaryDeviceRoleRequest,
    PrimaryDevicesApi,
)
from nli_engine.engine.tools.spec import ToolSpec

PRIMARY_DEVICES_MUTATION_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="add_primary_smartphone",
        api_class=PrimaryDevicesApi,
        method="add_smartphone_primary_device",
        request_model=PrimaryDeviceRoleRequest,
        description="Add a smartphone as a primary device role.",
    ),
    ToolSpec(
        name="add_primary_web_browser",
        api_class=PrimaryDevicesApi,
        method="add_web_browser_primary_device",
        request_model=PrimaryDeviceRoleRequest,
        description="Add a web browser as a primary device role.",
    ),
]

PRIMARY_DEVICES_READ_ONLY_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="get_primary_devices",
        api_class=PrimaryDevicesApi,
        method="get_primary_devices",
        description="Return all primary device roles added so far.",
    ),
]
