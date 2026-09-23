from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

import litellm
from pydantic import BaseModel

_log = logging.getLogger("nli_engine.llm")

T = TypeVar("T", bound=BaseModel)


def _completion_or_log(kwargs: dict[str, Any], model: str) -> Any:
    """Call ``litellm.completion`` and emit an ``llm_error`` event on failure.

    The exception is re-raised after logging so upstream behaviour is unchanged;
    the log event exists solely to leave a diagnostic trail in the session JSONL.
    """
    try:
        return litellm.completion(**kwargs)
    except Exception as exc:
        _log.error(
            "llm_error",
            extra={
                "event": "llm_error",
                "model": model,
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        raise


@dataclass(frozen=True)
class ToolCall:
    """A single tool invocation returned by the LLM.

    Attributes:
        id: Opaque call identifier used to match tool results back to calls.
        name: Function name; matches a BoundTool.name in the tool map.
        arguments: Decoded JSON arguments ready to pass to the tool's request_model.
    """

    id: str
    name: str
    arguments: dict


@dataclass(frozen=True)
class LLMResponse:
    """Typed return value of LLMClient.complete().

    Attributes:
        text: LLM text output; None when the response consists solely of tool calls.
        tool_calls: Parsed tool invocations; empty list when the LLM produced text.
        input_tokens: Prompt token count.
        output_tokens: Completion token count.
    """

    text: str | None
    tool_calls: list[ToolCall]
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class StructuredResponse(Generic[T]):
    """Return value of LLMClient.complete_structured().

    Attributes:
        parsed: The Pydantic model instance parsed from the response.
        input_tokens: Prompt token count.
        output_tokens: Completion token count.
    """

    parsed: T
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class LLMClient:
    """Provider-agnostic LLM client backed by LiteLLM.

    The provider endpoint is configured via the ``OPENAI_API_BASE`` environment
    variable, which LiteLLM reads automatically. Set it in ``.env`` when
    targeting a non-default endpoint (e.g. a local Ollama instance).

    Attributes:
        model: LiteLLM model identifier, e.g. ``"ollama/qwen2.5:7b"`` or ``"gpt-4o"``.
        temperature: Sampling temperature forwarded to the provider. ``None``
            leaves it unset so the provider applies its own default.
    """

    model: str
    temperature: float | None = None

    def complete(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        """Send a chat completion request and return the parsed response.

        Args:
            messages: Conversation history in OpenAI message-dict format.
            tools: Tool schemas in OpenAI function-calling format.
                Passed to the provider only when non-empty.

        Returns:
            Parsed LLMResponse with text, tool calls, and token counts.
        """
        kwargs: dict = {"model": self.model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature

        raw = _completion_or_log(kwargs, self.model)
        choice = raw.choices[0].message

        parsed_calls: list[ToolCall] = []
        if choice.tool_calls:
            for tc in choice.tool_calls:
                parsed_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments or "{}"),
                    )
                )

        return LLMResponse(
            text=choice.content,
            tool_calls=parsed_calls,
            input_tokens=raw.usage.prompt_tokens,
            output_tokens=raw.usage.completion_tokens,
        )

    def complete_structured(
        self, messages: list[dict], schema: type[T]
    ) -> StructuredResponse[T]:
        """Send a structured-output completion request and return the parsed model.

        No tools are sent. The provider is asked to respond with JSON that
        conforms to ``schema``'s JSON schema. LiteLLM passes ``response_format``
        directly to the provider (OpenAI JSON schema mode or equivalent).

        Args:
            messages: Conversation history in OpenAI message-dict format.
            schema: Pydantic model class defining the expected response shape.

        Returns:
            StructuredResponse with the parsed model instance and token counts.
        """
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "response_format": schema,
        }
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature

        raw = _completion_or_log(kwargs, self.model)
        choice = raw.choices[0].message
        parsed = schema.model_validate_json(choice.content)
        return StructuredResponse(
            parsed=parsed,
            input_tokens=raw.usage.prompt_tokens,
            output_tokens=raw.usage.completion_tokens,
        )
