"""Tests for assembly-unit retry logic in OneShotLLMWorkflow.run_turn()."""

from __future__ import annotations

from unittest.mock import MagicMock

from nli_engine.engine.workflow.assembly import (
    AssemblyPlan,
    AssemblyUnit,
    OrchestratorResult,
)
from nli_engine.engine.workflow.log import StepLog
from nli_engine.engine.workflow.workflows.one_shot_llm import OneShotLLMWorkflow


def _make_log(name: str = "test") -> StepLog:
    return StepLog(
        step_name=name, model=None, input_tokens=0, output_tokens=0, latency_ms=0.0
    )


def _ok_result() -> OrchestratorResult:
    return OrchestratorResult(success=True)


def _fail_result(issues: list[str]) -> OrchestratorResult:
    return OrchestratorResult(success=False, open_questions=issues)


def _make_workflow(
    units: list[AssemblyUnit] | None = None,
    max_unit_retries: int = 1,
) -> OneShotLLMWorkflow:
    """Build a OneShotLLMWorkflow instance with all steps replaced by mocks.

    Bypasses __init__ via object.__new__ and sets only the attributes that
    run_turn() reads. Steps are MagicMock instances whose return values can be
    overridden per test.
    """
    wf: OneShotLLMWorkflow = object.__new__(OneShotLLMWorkflow)

    config = MagicMock()
    config.parameters = {"max_unit_retries": max_unit_retries}
    wf.config = config

    wf._session = MagicMock()
    wf._session.serialize.return_value = {}

    # Retrieval is not exercised here; run_turn checks _retriever to decide
    # whether to splice retrieve_docs into the setup step's tools.
    wf._retriever = None

    # run_turn clears and drains this list around the orchestrator step.
    wf._specialist_logs = []

    plan = AssemblyPlan(
        units=units
        or [
            AssemblyUnit(
                name="Unit 1", description="desc", needs_connected_device=False
            )
        ]
    )

    wf._refinement_step = MagicMock()
    wf._refinement_step.run.return_value = ("refined", _make_log("refiner"))

    wf._planning_step = MagicMock()
    wf._planning_step.run.return_value = ("plan", _make_log("planner"))

    wf._extraction_step = MagicMock()
    wf._extraction_step.run.return_value = (plan, _make_log("extractor"))

    wf._setup_step = MagicMock()
    wf._setup_step.run.return_value = ("", _make_log("setup"))

    wf._orchestrator_step = MagicMock()
    wf._orchestrator_step.tool_names = []

    wf._orchestrator_result_step = MagicMock()

    wf._explainer_step = MagicMock()
    wf._explainer_step.run.return_value = (
        "user-friendly explanation",
        _make_log("explainer"),
    )

    # Shadow the tool-resolution methods — tests exercise the retry loop, not tool wiring.
    wf._tools_for_names = MagicMock(return_value=[])  # type: ignore[method-assign]
    wf._resolve_tools = MagicMock(return_value=[])  # type: ignore[method-assign]

    return wf


# ---------------------------------------------------------------------------
# Success on first attempt
# ---------------------------------------------------------------------------


def test_success_on_first_attempt_makes_one_orchestrator_call() -> None:
    wf = _make_workflow()
    wf._orchestrator_step.run.return_value = ("summary ok", _make_log("orchestrator"))
    wf._orchestrator_result_step.run.return_value = (
        _ok_result(),
        _make_log("orchestrator_result"),
    )

    from nli_engine.engine.workflow.workflows.one_shot_llm import (
        OneShotLLMWorkflowContext,
    )

    result = wf.run_turn("build a study", OneShotLLMWorkflowContext())

    assert wf._orchestrator_step.run.call_count == 1
    assert result.partial_failures == []
    assert result.done is True


# ---------------------------------------------------------------------------
# Retry on failure then success
# ---------------------------------------------------------------------------


def test_retry_on_failure_then_success() -> None:
    wf = _make_workflow(max_unit_retries=1)
    wf._orchestrator_step.run.side_effect = [
        ("summary fail", _make_log("orchestrator")),
        ("summary ok", _make_log("orchestrator")),
    ]
    wf._orchestrator_result_step.run.side_effect = [
        (
            _fail_result(["mobilenetwork not supported"]),
            _make_log("orchestrator_result"),
        ),
        (_ok_result(), _make_log("orchestrator_result")),
    ]

    from nli_engine.engine.workflow.workflows.one_shot_llm import (
        OneShotLLMWorkflowContext,
    )

    result = wf.run_turn("build a study", OneShotLLMWorkflowContext())

    assert wf._orchestrator_step.run.call_count == 2
    assert wf._orchestrator_result_step.run.call_count == 2
    assert result.partial_failures == []


def test_retry_message_contains_open_questions() -> None:
    """The injected retry message must quote the issues from the failed attempt."""
    wf = _make_workflow(max_unit_retries=1)
    wf._orchestrator_step.run.side_effect = [
        ("summary fail", _make_log()),
        ("summary ok", _make_log()),
    ]
    wf._orchestrator_result_step.run.side_effect = [
        (_fail_result(["measure X not found"]), _make_log()),
        (_ok_result(), _make_log()),
    ]

    from nli_engine.engine.workflow.workflows.one_shot_llm import (
        OneShotLLMWorkflowContext,
    )

    ctx = OneShotLLMWorkflowContext()
    wf.run_turn("build a study", ctx)

    # The retry user message must mention the issue text.
    messages = [m.content for m in ctx.history if m.role == "user"]
    retry_messages = [m for m in messages if "incomplete" in m.lower()]
    assert len(retry_messages) == 1
    assert "measure X not found" in retry_messages[0]


# ---------------------------------------------------------------------------
# All retries exhausted → partial_failures
# ---------------------------------------------------------------------------


def test_all_retries_exhausted_records_partial_failure() -> None:
    wf = _make_workflow(max_unit_retries=1)
    wf._orchestrator_step.run.return_value = ("summary fail", _make_log("orchestrator"))
    wf._orchestrator_result_step.run.return_value = (
        _fail_result(["task not created"]),
        _make_log("orchestrator_result"),
    )

    from nli_engine.engine.workflow.workflows.one_shot_llm import (
        OneShotLLMWorkflowContext,
    )

    result = wf.run_turn("build a study", OneShotLLMWorkflowContext())

    assert len(result.partial_failures) == 1
    assert "Unit 1" in result.partial_failures[0]
    assert "task not created" in result.partial_failures[0]


def test_exhausted_unit_does_not_block_subsequent_units() -> None:
    units = [
        AssemblyUnit(name="Unit 1", description="desc 1", needs_connected_device=False),
        AssemblyUnit(name="Unit 2", description="desc 2", needs_connected_device=False),
    ]
    wf = _make_workflow(units=units, max_unit_retries=1)

    # Unit 1 always fails; Unit 2 always succeeds.
    wf._orchestrator_step.run.side_effect = [
        ("fail", _make_log()),
        ("fail", _make_log()),  # retry
        ("ok", _make_log()),  # unit 2
    ]
    wf._orchestrator_result_step.run.side_effect = [
        (_fail_result(["issue"]), _make_log()),
        (_fail_result(["issue"]), _make_log()),
        (_ok_result(), _make_log()),
    ]

    from nli_engine.engine.workflow.workflows.one_shot_llm import (
        OneShotLLMWorkflowContext,
    )

    result = wf.run_turn("build a study", OneShotLLMWorkflowContext())

    assert len(result.partial_failures) == 1
    assert "Unit 1" in result.partial_failures[0]
    assert wf._orchestrator_step.run.call_count == 3


# ---------------------------------------------------------------------------
# OrchestratorResult model
# ---------------------------------------------------------------------------


def test_orchestrator_result_success_default_empty_open_questions() -> None:
    r = OrchestratorResult(success=True)
    assert r.open_questions == []


def test_orchestrator_result_failure_preserves_issues() -> None:
    r = OrchestratorResult(success=False, open_questions=["a", "b"])
    assert r.success is False
    assert r.open_questions == ["a", "b"]
