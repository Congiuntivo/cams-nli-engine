from nli_engine.client._generated.authoring_client import (
    CronScheduledTriggerRequest,
    DelayedTriggerRequest,
    ImmediateTriggerRequest,
    ManualTriggerRequest,
    NoOpTriggerRequest,
    PeriodicTriggerRequest,
    TriggersApi,
)
from nli_engine.engine.tools.spec import ToolSpec

TRIGGERS_MUTATION_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="add_immediate_trigger",
        api_class=TriggersApi,
        method="add_immediate_trigger",
        request_model=ImmediateTriggerRequest,
        description="Add a trigger that fires immediately when the study starts.",
    ),
    ToolSpec(
        name="add_delayed_trigger",
        api_class=TriggersApi,
        method="add_delayed_trigger",
        request_model=DelayedTriggerRequest,
        description="Add a trigger that fires once after a fixed delay.",
    ),
    ToolSpec(
        name="add_periodic_trigger",
        api_class=TriggersApi,
        method="add_periodic_trigger",
        request_model=PeriodicTriggerRequest,
        description="Add a trigger that fires repeatedly at a fixed interval.",
    ),
    ToolSpec(
        name="add_cron_trigger",
        api_class=TriggersApi,
        method="add_cron_scheduled_trigger",
        request_model=CronScheduledTriggerRequest,
        description="Add a cron-scheduled trigger (minute/hour/day/month/weekday).",
    ),
    ToolSpec(
        name="add_manual_trigger",
        api_class=TriggersApi,
        method="add_manual_trigger",
        request_model=ManualTriggerRequest,
        description="Add a trigger that fires when manually activated by the researcher.",
    ),
    ToolSpec(
        name="add_no_op_trigger",
        api_class=TriggersApi,
        method="add_no_op_trigger",
        request_model=NoOpTriggerRequest,
        description="Add a no-op placeholder trigger.",
    ),
]

TRIGGERS_READ_ONLY_TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="get_triggers",
        api_class=TriggersApi,
        method="get_triggers",
        description="Return all triggers added so far.",
    ),
]
