from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from nli_engine.client._generated.authoring_client.exceptions import ApiException
from nli_engine.engine.tools import BoundTool

# 4xx statuses represent bad LLM arguments the model can correct.
_RETRYABLE_STATUSES: frozenset[int] = frozenset({400, 404, 409, 422})


@dataclass(frozen=True)
class ToolResult:
    """Result of a tool call — either a success payload or a classified error.

    Attributes:
        content: Serialised success output or formatted error message; always
            safe to include verbatim in an LLM tool-result message.
        is_error: True when the tool call failed.
        retryable: Meaningful only when ``is_error`` is True. True for 4xx
            errors the LLM caused and can correct; False for 5xx and auth
            failures where the session cannot recover.
    """

    content: str
    is_error: bool = False
    retryable: bool = True

    @classmethod
    def success(cls, content: str) -> ToolResult:
        """Wrap a successful tool output."""
        return cls(content=content)

    @classmethod
    def error(cls, message: str, *, retryable: bool) -> ToolResult:
        """Wrap a tool failure with a retryability classification."""
        return cls(content=message, is_error=True, retryable=retryable)


def _serialize(result: Any) -> str:
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


def _format_api_error(exc: ApiException) -> str:
    try:
        body = json.loads(exc.body)
        message = body.get("error", exc.body)
    except (json.JSONDecodeError, AttributeError, TypeError):
        message = exc.body or exc.reason
    return f"Error ({exc.status}): {message}"


def call_tool(tool: BoundTool, arguments: dict) -> ToolResult:
    """Execute a BoundTool from LLM-returned arguments and return a typed result.

    For read-only tools (``request_model is None``) the tool is called with no
    arguments. For mutation tools the arguments dict is used to instantiate the
    request_model, which Pydantic validates before the call is dispatched.

    API errors are caught and classified: 4xx errors are retryable (the LLM
    can correct its arguments); 5xx and auth failures are not.

    Args:
        tool: The bound tool to execute.
        arguments: Decoded JSON arguments from the LLM's tool call.

    Returns:
        ToolResult with the serialised output or a formatted error message.
    """
    try:
        if tool.request_model is None:
            raw = tool.call()
        else:
            raw = tool.call(tool.request_model(**arguments))
        return ToolResult.success(_serialize(raw))
    except ApiException as exc:
        return ToolResult.error(
            _format_api_error(exc),
            retryable=exc.status in _RETRYABLE_STATUSES,
        )
