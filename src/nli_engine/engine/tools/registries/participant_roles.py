from nli_engine.client._generated.authoring_client import (
    AddParticipantRoleRequest,
    ParticipantRolesApi,
)
from nli_engine.engine.tools.spec import ToolSpec

PARTICIPANT_ROLES_MUTATION_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="add_participant_role",
        api_class=ParticipantRolesApi,
        method="add_participant_role",
        request_model=AddParticipantRoleRequest,
        description="Add a participant role to the protocol.",
    ),
]

PARTICIPANT_ROLES_READ_ONLY_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="get_participant_roles",
        api_class=ParticipantRolesApi,
        method="get_participant_roles",
        description="Return all participant roles added so far.",
    ),
]
