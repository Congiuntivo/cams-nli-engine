from __future__ import annotations

import json
from typing import Any

from nli_engine.engine.tools import BoundTool


def call_tool(tool: BoundTool, arguments: dict) -> str:
    """Execute a BoundTool from LLM-returned arguments and return a string result.

    For read-only tools (``request_model is None``) the tool is called with no
    arguments. For mutation tools the arguments dict is used to instantiate the
    request_model, which Pydantic validates before the call is dispatched.

    Args:
        tool: The bound tool to execute.
        arguments: Decoded JSON arguments from the LLM's tool call.

    Returns:
        Serialised result as a string suitable for inclusion in a tool-result
        message. None results become ``"ok"``; Pydantic models are JSON-encoded.
    """
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
