from nli_engine.client._generated.authoring_client import (
    DevicesApi,
    ESenseDeviceRequest,
    MovesenseDeviceRequest,
    MovisensDeviceRequest,
    PolarDeviceRequest,
)
from nli_engine.engine.tools.spec import ToolSpec

DEVICES_MUTATION_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="add_esense",
        api_class=DevicesApi,
        method="add_e_sense_device",
        request_model=ESenseDeviceRequest,
        description="Add an eSense earbud device.",
    ),
    ToolSpec(
        name="add_movesense",
        api_class=DevicesApi,
        method="add_movesense_device",
        request_model=MovesenseDeviceRequest,
        description="Add a Movesense device.",
    ),
    ToolSpec(
        name="add_movisens",
        api_class=DevicesApi,
        method="add_movisens_device",
        request_model=MovisensDeviceRequest,
        description="Add a Movisens device.",
    ),
    ToolSpec(
        name="add_polar",
        api_class=DevicesApi,
        method="add_polar_device",
        request_model=PolarDeviceRequest,
        description="Add a Polar heart-rate device.",
    ),
]

DEVICES_READ_ONLY_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="get_connected_devices",
        api_class=DevicesApi,
        method="get_device_roles",
        description="Return all connected (wearable) device roles added so far.",
    ),
]
