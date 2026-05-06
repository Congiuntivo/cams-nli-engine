from __future__ import annotations

import json
from unittest.mock import MagicMock

from pydantic import BaseModel

from nli_engine.client._generated.authoring_client.exceptions import (
    BadRequestException,
    ServiceException,
    UnauthorizedException,
)
from nli_engine.engine.llm.dispatch import ToolResult, call_tool
from nli_engine.engine.tools import BoundTool


class _DummyRequest(BaseModel):
    value: str


def _make_tool(request_model=_DummyRequest, call_return=None, call_side_effect=None):
    mock_call = MagicMock(return_value=call_return, side_effect=call_side_effect)
    return BoundTool(
        name="dummy",
        description="A dummy tool",
        request_model=request_model,
        call=mock_call,
    )


# ---------------------------------------------------------------------------
# Success path
# ---------------------------------------------------------------------------


def test_call_tool_success_none_result():
    tool = _make_tool(call_return=None)
    result = call_tool(tool, {"value": "x"})
    assert result == ToolResult.success("ok")


def test_call_tool_success_string_result():
    tool = _make_tool(call_return="created")
    result = call_tool(tool, {"value": "x"})
    assert result == ToolResult.success("created")


def test_call_tool_success_pydantic_result():
    class _Response(BaseModel):
        id: str

    tool = _make_tool(call_return=_Response(id="abc"))
    result = call_tool(tool, {"value": "x"})
    assert not result.is_error
    assert json.loads(result.content) == {"id": "abc"}


def test_call_tool_read_only_tool():
    tool = _make_tool(request_model=None, call_return="data")
    result = call_tool(tool, {})
    assert result == ToolResult.success("data")


# ---------------------------------------------------------------------------
# Pydantic validation errors (retryable — bad LLM arguments)
# ---------------------------------------------------------------------------


def test_call_tool_validation_error_is_retryable():
    class _StrictRequest(BaseModel):
        value: int

    tool = _make_tool(request_model=_StrictRequest)
    result = call_tool(tool, {"value": "not-an-int"})

    assert result.is_error
    assert result.retryable
    assert "validation error" in result.content.lower()


# ---------------------------------------------------------------------------
# Retryable errors (4xx)
# ---------------------------------------------------------------------------


def test_call_tool_bad_request_is_retryable():
    exc = BadRequestException(
        status=400,
        reason="Bad Request",
        body=json.dumps({"error": "Unsupported measureType: steps"}),
    )
    tool = _make_tool(call_side_effect=exc)
    result = call_tool(tool, {"value": "x"})

    assert result.is_error
    assert result.retryable
    assert "400" in result.content
    assert "Unsupported measureType: steps" in result.content


def test_call_tool_bad_request_non_json_body():
    exc = BadRequestException(status=400, reason="Bad Request", body="plain text error")
    tool = _make_tool(call_side_effect=exc)
    result = call_tool(tool, {"value": "x"})

    assert result.is_error
    assert result.retryable
    assert "plain text error" in result.content


# ---------------------------------------------------------------------------
# Non-retryable errors (5xx, auth)
# ---------------------------------------------------------------------------


def test_call_tool_server_error_is_not_retryable():
    exc = ServiceException(status=500, reason="Internal Server Error", body=None)
    tool = _make_tool(call_side_effect=exc)
    result = call_tool(tool, {"value": "x"})

    assert result.is_error
    assert not result.retryable
    assert "500" in result.content


def test_call_tool_unauthorized_is_not_retryable():
    exc = UnauthorizedException(status=401, reason="Unauthorized", body=None)
    tool = _make_tool(call_side_effect=exc)
    result = call_tool(tool, {"value": "x"})

    assert result.is_error
    assert not result.retryable
