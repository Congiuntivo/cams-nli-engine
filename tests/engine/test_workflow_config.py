import textwrap
from pathlib import Path

import pytest

from nli_engine.engine.workflow.config import WorkflowConfig


def test_config_defaults_to_empty_dicts() -> None:
    config = WorkflowConfig()
    assert config.models == {}
    assert config.parameters == {}


def test_config_accepts_explicit_values() -> None:
    config = WorkflowConfig(
        models={"executor": "claude-sonnet-4-6"},
        parameters={"max_turns": 10},
    )
    assert config.models["executor"] == "claude-sonnet-4-6"
    assert config.parameters["max_turns"] == 10


def test_from_yaml_loads_valid_file(tmp_path: Path) -> None:
    yaml_file = tmp_path / "workflow.yaml"
    yaml_file.write_text(
        textwrap.dedent("""\
            models:
              refinement: claude-haiku-4-5-20251001
              executor: claude-sonnet-4-6
            parameters:
              max_history_turns: 50
        """)
    )
    config = WorkflowConfig.from_yaml(yaml_file)
    assert config.models["refinement"] == "claude-haiku-4-5-20251001"
    assert config.models["executor"] == "claude-sonnet-4-6"
    assert config.parameters["max_history_turns"] == 50


def test_from_yaml_accepts_string_path(tmp_path: Path) -> None:
    yaml_file = tmp_path / "workflow.yaml"
    yaml_file.write_text("models:\n  executor: claude-sonnet-4-6\n")
    config = WorkflowConfig.from_yaml(str(yaml_file))
    assert config.models["executor"] == "claude-sonnet-4-6"


def test_from_yaml_empty_file_returns_defaults(tmp_path: Path) -> None:
    yaml_file = tmp_path / "empty.yaml"
    yaml_file.write_text("")
    config = WorkflowConfig.from_yaml(yaml_file)
    assert config.models == {}
    assert config.parameters == {}


def test_from_yaml_partial_keys_fill_defaults(tmp_path: Path) -> None:
    yaml_file = tmp_path / "partial.yaml"
    yaml_file.write_text("models:\n  executor: claude-sonnet-4-6\n")
    config = WorkflowConfig.from_yaml(yaml_file)
    assert config.parameters == {}


def test_from_yaml_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        WorkflowConfig.from_yaml("/nonexistent/path/workflow.yaml")
