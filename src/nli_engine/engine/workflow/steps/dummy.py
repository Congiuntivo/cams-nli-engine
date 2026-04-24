import time

from nli_engine.client._generated.authoring_client import (
    AddParticipantRoleRequest,
    DataEndpointRequest,
    PrimaryDeviceRoleRequest,
)
from nli_engine.engine.tools import BoundTool
from nli_engine.engine.workflow.base import Step, WorkflowContext
from nli_engine.engine.workflow.log import StepLog


class DummySetupStep(Step):
    def __init__(self) -> None:
        super().__init__(
            name="dummy_setup",
            tool_names=[
                "add_primary_smartphone",
                "add_data_endpoint",
                "add_participant_role",
            ],
        )

    def run(
        self, context: WorkflowContext, tools: list[BoundTool]
    ) -> tuple[str, StepLog]:
        start = time.perf_counter()
        by_name = {t.name: t for t in tools}

        by_name["add_primary_smartphone"].call(
            PrimaryDeviceRoleRequest(role_name="Smartphone")
        )
        by_name["add_data_endpoint"].call(
            DataEndpointRequest(endpoint_type="CAWS", name="default")
        )
        by_name["add_participant_role"].call(
            AddParticipantRoleRequest(role_name="Participant")
        )

        log = StepLog(
            step_name=self.name,
            model=None,
            input_tokens=0,
            output_tokens=0,
            latency_ms=(time.perf_counter() - start) * 1000,
        )
        return ("setup complete", log)
