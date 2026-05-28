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
from nli_engine.engine.tools.registries.services import (
    SERVICES_READ_ONLY_TOOLS,
    SERVICES_TOOLS,
)
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
from nli_engine.engine.tools.spec import ToolSpec

# ---------------------------------------------------------------------------
# Specialist tool-name sets
# Each set defines the BoundTools a specialist step may call. Names must
# match entries in TOOL_REGISTRY exactly.
# ---------------------------------------------------------------------------

SETUP_SPECIALIST_TOOL_NAMES: list[str] = [
    "add_data_endpoint",
    "add_participant_role",
    "get_participant_roles",
    "add_primary_smartphone",
    "add_primary_web_browser",
    "get_primary_devices",
    "add_expected_data_all_roles",
    "add_expected_data_for_role",
]

DEVICE_SPECIALIST_TOOL_NAMES: list[str] = [
    "add_esense",
    "add_movesense",
    "add_movisens",
    "add_polar",
    "get_connected_devices",
    "add_air_quality_service",
    "add_health_service",
    "add_weather_service",
    "add_location_service",
]

TRIGGER_SPECIALIST_TOOL_NAMES: list[str] = [
    "add_immediate_trigger",
    "add_delayed_trigger",
    "add_periodic_trigger",
    "add_cron_trigger",
    "add_manual_trigger",
    "add_no_op_trigger",
    "add_date_time_trigger",
    "add_elapsed_time_trigger",
    "add_no_user_task_trigger",
    "add_one_time_trigger",
    "add_passive_trigger",
    "add_random_recurrent_trigger",
    "add_recurrent_scheduled_trigger",
    "add_sampling_event_trigger",
    "add_scheduled_trigger",
    "add_user_task_trigger",
    "get_triggers",
]

TASK_SPECIALIST_TOOL_NAMES: list[str] = [
    "add_background_task",
    "add_app_task",
    "add_health_app_task",
    "add_web_task",
    "get_tasks",
]

TASK_CONTROL_ASSEMBLER_TOOL_NAMES: list[str] = [
    "add_task_control",
    "get_task_controls",
    # Cross-domain reads to verify referenced entities before creating the binding.
    "get_triggers",
    "get_tasks",
    "get_primary_devices",
    "get_connected_devices",
    "get_services",
]

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
    *SERVICES_READ_ONLY_TOOLS,
    *PARTICIPANT_ROLES_READ_ONLY_TOOLS,
    *TASKS_READ_ONLY_TOOLS,
    *TRIGGERS_READ_ONLY_TOOLS,
    *TASK_CONTROLS_READ_ONLY_TOOLS,
]
