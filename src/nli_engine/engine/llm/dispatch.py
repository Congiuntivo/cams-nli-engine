from __future__ import annotations

import json
from typing import Any

from nli_engine.engine.tools import BoundTool


def call_tool(tool: BoundTool, arguments: dict) -> str:
    if tool.request_model is None:
        result: Any = tool.call()
    else:
        result = tool.call(tool.request_model(**arguments))

    if result is None:
        return "ok"
    if isinstance(result, str):
        return result
    if hasattr(result, "model_dump"):
        return json.dumps(result.model_dump())
    try:
        return json.dumps(result)
    except (TypeError, ValueError):
        return str(result)
