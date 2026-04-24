from typing import Any

from pydantic import BaseModel

from nli_engine.engine.workflow.log import StepLog


class TurnResult(BaseModel, frozen=True):
    message: str
    logs: list[StepLog]
    done: bool
    protocol: dict[str, Any] | None = None
