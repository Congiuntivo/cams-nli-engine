from __future__ import annotations

from dataclasses import dataclass, field

import json
import litellm


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass(frozen=True)
class LLMResponse:
    text: str | None
    tool_calls: list[ToolCall]
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class LLMClient:
    model: str
    api_base: str | None = field(default=None)

    def complete(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        kwargs: dict = {"model": self.model, "messages": messages}
        if self.api_base is not None:
            kwargs["api_base"] = self.api_base
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
