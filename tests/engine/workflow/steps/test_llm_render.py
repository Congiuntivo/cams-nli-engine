from unittest.mock import MagicMock

import pytest

from nli_engine.engine.workflow.base import WorkflowContext
from nli_engine.engine.workflow.steps.llm import LLMStep


class _ConcreteContext(WorkflowContext):
    pass


class _ContextWithVariables(WorkflowContext):
    def context_variables(self) -> dict[str, str]:
        return {"foo": "bar", "count": "42"}


def _make_step(system_prompt: str) -> LLMStep:
    client = MagicMock()
    client.model = "test-model"
    return LLMStep(name="test", client=client, system_prompt=system_prompt)


def test_prompt_without_tags_is_returned_unchanged() -> None:
    step = _make_step("Hello world")
    ctx = _ConcreteContext()
    assert step._render_system_prompt(ctx) == "Hello world"


def test_var_tag_is_substituted() -> None:
    step = _make_step("prefix {{var: foo}} suffix")
    ctx = _ContextWithVariables()
    assert step._render_system_prompt(ctx) == "prefix bar suffix"


def test_multiple_var_tags_are_substituted() -> None:
    step = _make_step("{{var: foo}} and {{var: count}}")
    ctx = _ContextWithVariables()
    assert step._render_system_prompt(ctx) == "bar and 42"


def test_whitespace_in_tag_is_tolerated() -> None:
    step = _make_step("{{var:foo}}")
    ctx = _ContextWithVariables()
    assert step._render_system_prompt(ctx) == "bar"


def test_undefined_variable_raises_value_error() -> None:
    step = _make_step("{{var: missing}}")
    ctx = _ContextWithVariables()
    with pytest.raises(ValueError, match="missing"):
        step._render_system_prompt(ctx)


def test_base_context_with_no_variables_and_no_tags() -> None:
    step = _make_step("plain prompt")
    ctx = _ConcreteContext()
    assert step._render_system_prompt(ctx) == "plain prompt"


def test_base_context_raises_on_any_var_tag() -> None:
    step = _make_step("{{var: anything}}")
    ctx = _ConcreteContext()
    with pytest.raises(ValueError):
        step._render_system_prompt(ctx)
