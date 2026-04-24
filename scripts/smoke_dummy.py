"""Smoke test for DummyWorkflow against a live server (default: localhost:8080)."""

import sys

from nli_engine.engine.client import build_client
from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.workflows.dummy import (
    DummyWorkflow,
    DummyWorkflowContext,
)


def main(base_url: str = "http://localhost:8080") -> None:
    session = ProtocolSession(build_client(base_url), name="Dummy Protocol")
    wf = DummyWorkflow(config=WorkflowConfig(), session=session)
    context = DummyWorkflowContext()

    response, logs = wf.run_turn("run setup", context)

    print(response)
    print("\n--- step logs ---")
    for log in logs:
        print(f"  {log.step_name}: {log.latency_ms:.1f}ms")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    main(url)
