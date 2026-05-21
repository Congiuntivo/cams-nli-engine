from __future__ import annotations

import json
from dataclasses import dataclass

import litellm


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
class LLMClient:
    """Provider-agnostic LLM client backed by LiteLLM.

    The provider endpoint is configured via the ``OPENAI_API_BASE`` environment
    variable, which LiteLLM reads automatically. Set it in ``.env`` when
    targeting a non-default endpoint (e.g. a local Ollama instance).

    Attributes:
        model: LiteLLM model identifier, e.g. ``"ollama/qwen2.5:7b"`` or ``"gpt-4o"``.
    """

    model: str

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

        raw = litellm.completion(**kwargs)
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
