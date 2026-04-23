from nli_engine.engine.tools.spec import ToolSpec
from nli_engine.engine.tools.registries.data_endpoint import DATA_ENDPOINT_TOOLS
from nli_engine.engine.tools.registries.devices import (
    DEVICES_MUTATION_TOOLS,
    DEVICES_READ_ONLY_TOOLS,
)
from nli_engine.engine.tools.registries.expected_participant_data import (
    EXPECTED_PARTICIPANT_DATA_TOOLS,
)
from nli_engine.engine.tools.registries.participant_roles import (
    PARTICIPANT_ROLES_MUTATION_TOOLS,
    PARTICIPANT_ROLES_READ_ONLY_TOOLS,
)
from nli_engine.engine.tools.registries.primary_devices import (
    PRIMARY_DEVICES_MUTATION_TOOLS,
    PRIMARY_DEVICES_READ_ONLY_TOOLS,
)
from nli_engine.engine.tools.registries.requirements_and_serialization import (
    REQUIREMENTS_AND_SERIALIZATION_READ_ONLY_TOOLS,
)
from nli_engine.engine.tools.registries.services import SERVICES_TOOLS
from nli_engine.engine.tools.registries.task_controls import (
    TASK_CONTROLS_MUTATION_TOOLS,
    TASK_CONTROLS_READ_ONLY_TOOLS,
)
from nli_engine.engine.tools.registries.tasks import (
    TASKS_MUTATION_TOOLS,
    TASKS_READ_ONLY_TOOLS,
)
from nli_engine.engine.tools.registries.triggers import (
    TRIGGERS_MUTATION_TOOLS,
    TRIGGERS_READ_ONLY_TOOLS,
)

TOOL_REGISTRY: list[ToolSpec] = [
    # Devices — primary
    *PRIMARY_DEVICES_MUTATION_TOOLS,
    # Devices — connected wearables
    *DEVICES_MUTATION_TOOLS,
    # Participants
    *PARTICIPANT_ROLES_MUTATION_TOOLS,
    *EXPECTED_PARTICIPANT_DATA_TOOLS,
    # Services
    *SERVICES_TOOLS,
    # Data endpoint
    *DATA_ENDPOINT_TOOLS,
    # Tasks
    *TASKS_MUTATION_TOOLS,
    # Triggers
    *TRIGGERS_MUTATION_TOOLS,
    # Task controls
    *TASK_CONTROLS_MUTATION_TOOLS,
    # ------------------------------------------------------------------ #
    # Read-only inspection tools
    # ------------------------------------------------------------------ #
    *REQUIREMENTS_AND_SERIALIZATION_READ_ONLY_TOOLS,
    *PRIMARY_DEVICES_READ_ONLY_TOOLS,
    *DEVICES_READ_ONLY_TOOLS,
    *PARTICIPANT_ROLES_READ_ONLY_TOOLS,
    *TASKS_READ_ONLY_TOOLS,
    *TRIGGERS_READ_ONLY_TOOLS,
    *TASK_CONTROLS_READ_ONLY_TOOLS,
]
