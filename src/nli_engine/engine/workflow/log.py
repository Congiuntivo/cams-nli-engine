from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StepLog(BaseModel):
    model_config = ConfigDict(frozen=True)

    step_name: str
    model: str | None
    input_tokens: int
    output_tokens: int
    latency_ms: float
    extra: dict[str, Any] = Field(default_factory=dict)
