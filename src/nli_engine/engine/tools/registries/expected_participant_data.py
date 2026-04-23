from nli_engine.client._generated.authoring_client import (
    AddExpectedParticipantDataForRoleRequest,
    AddExpectedParticipantDataRequest,
    ExpectedParticipantDataApi,
)
from nli_engine.engine.tools.spec import ToolSpec

EXPECTED_PARTICIPANT_DATA_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="add_expected_data_all_roles",
        api_class=ExpectedParticipantDataApi,
        method="add_expected_participant_data_for_all_roles",
        request_model=AddExpectedParticipantDataRequest,
        description="Declare expected participant data for all roles.",
    ),
    ToolSpec(
        name="add_expected_data_for_role",
        api_class=ExpectedParticipantDataApi,
        method="add_expected_participant_data_for_role",
        request_model=AddExpectedParticipantDataForRoleRequest,
        description="Declare expected participant data for a specific role.",
    ),
]
