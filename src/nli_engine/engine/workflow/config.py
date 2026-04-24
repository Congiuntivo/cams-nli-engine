from __future__ import annotations
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class WorkflowConfig(BaseModel):
    models: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping from model purpose name to model identifier.",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters for the workflow."
    )

    @classmethod
    def from_yaml(cls, path: str | Path) -> WorkflowConfig:
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data or {})
