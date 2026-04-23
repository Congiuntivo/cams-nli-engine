from nli_engine.client._generated.authoring_client import (
    RequirementsAndSerializationApi,
)
from nli_engine.engine.tools.spec import ToolSpec

REQUIREMENTS_AND_SERIALIZATION_READ_ONLY_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="get_requirements",
        api_class=RequirementsAndSerializationApi,
        method="get_requirements",
        description="Return the list of currently unfulfilled protocol requirements.",
    ),
]
