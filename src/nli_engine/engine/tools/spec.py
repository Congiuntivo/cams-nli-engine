from dataclasses import dataclass
from typing import Any, Callable, Optional

from pydantic import BaseModel


@dataclass(frozen=True)
class ToolSpec:
    name: str
    api_class: type
    method: str
    description: str
    request_model: Optional[type[BaseModel]] = None


@dataclass
class BoundTool:
    name: str
    description: str
    # None for read-only tools; the LLM dispatcher checks this to decide call arity
    request_model: Optional[type[BaseModel]]
    # 0-arg for read-only tools, 1-arg (request instance) for mutation tools
    call: Callable[..., Any]
