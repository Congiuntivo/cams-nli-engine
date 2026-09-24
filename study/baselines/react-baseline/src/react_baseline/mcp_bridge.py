"""MCP client bridge: spawns and multiplexes the CAMS and retrieval MCP servers.

Uses lexically nested ``async with`` blocks instead of ``AsyncExitStack``. In
practice the stack-based variant deadlocked when both stdio subprocesses were
registered through method calls; nesting keeps the anyio task groups
lexically ordered inside a single async method, which the MCP SDK requires.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@dataclass
class ToolSpec:
    """One tool exposed to the LLM.

    Attributes:
        name: Tool name (matches the MCP tool name and the OpenAI tool name).
        description: Human-readable description shown to the LLM.
        input_schema: JSON schema for the tool's arguments.
        server: Which MCP server owns this tool (``"cams"`` or ``"retrieval"``).
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    server: str


class McpBridge:
    """Multiplexed client to the CAMS sidecar and the retrieval MCP server.

    Use via :meth:`run` — pass a coroutine that receives the initialised
    bridge. Both stdio subprocesses stay alive for the whole callback and are
    torn down on exit.

    Attributes:
        tools: The full list of ``ToolSpec``s exposed to the LLM. Populated
            once both MCP servers are initialised.
    """

    def __init__(
        self,
        carp_mcp_binary: str,
        retrieval_mcp_binary: str,
    ) -> None:
        """Configure the bridge without launching subprocesses.

        Args:
            carp_mcp_binary: Absolute path to the ``carp-mcp`` entrypoint.
            retrieval_mcp_binary: Absolute path to the
                ``react-baseline-retrieval-mcp`` entrypoint.
        """
        self._carp_mcp_binary = carp_mcp_binary
        self._retrieval_mcp_binary = retrieval_mcp_binary
        self._sessions: dict[str, ClientSession] = {}
        self._owner: dict[str, str] = {}
        self.tools: list[ToolSpec] = []

    async def run(
        self,
        body: Callable[["McpBridge"], Awaitable[None]],
    ) -> None:
        """Open both MCP servers, invoke ``body(self)``, then close them.

        Args:
            body: Async callable executed with both MCP sessions live.
        """
        cams_params = StdioServerParameters(
            command=self._carp_mcp_binary,
            args=[],
            env={**os.environ},
        )
        retrieval_params = StdioServerParameters(
            command=self._retrieval_mcp_binary,
            args=[],
            env={**os.environ},
        )

        async with stdio_client(cams_params) as (r1, w1):
            async with ClientSession(r1, w1) as cams:
                await cams.initialize()
                await self._collect("cams", cams)

                async with stdio_client(retrieval_params) as (r2, w2):
                    async with ClientSession(r2, w2) as retrieval:
                        await retrieval.initialize()
                        await self._collect("retrieval", retrieval)

                        await body(self)

    async def _collect(self, name: str, session: ClientSession) -> None:
        self._sessions[name] = session
        listing = await session.list_tools()
        for tool in listing.tools:
            schema = getattr(tool, "inputSchema", None) or getattr(
                tool, "input_schema", None
            )
            self.tools.append(
                ToolSpec(
                    name=tool.name,
                    description=tool.description or "",
                    input_schema=schema or {"type": "object", "properties": {}},
                    server=name,
                )
            )
            self._owner[tool.name] = name

    async def call(self, tool_name: str, arguments: dict[str, Any]) -> tuple[str, bool]:
        """Invoke a tool on whichever MCP server owns it.

        Args:
            tool_name: Name of the tool to call.
            arguments: Arguments dict.

        Returns:
            ``(text_result, is_error)``. ``text_result`` concatenates the
            content blocks returned by the tool.
        """
        server = self._owner.get(tool_name)
        if server is None:
            return (f"Unknown tool: {tool_name}", True)

        session = self._sessions[server]
        result = await session.call_tool(tool_name, arguments=arguments)

        text_parts: list[str] = []
        for block in result.content:
            text = getattr(block, "text", None)
            if text is not None:
                text_parts.append(text)
        text = "\n".join(text_parts) if text_parts else ""
        is_error = getattr(result, "isError", None)
        if is_error is None:
            is_error = getattr(result, "is_error", False)
        return (text, bool(is_error))

    def openai_tools(self) -> list[dict[str, Any]]:
        """Return the aggregated tools formatted for the OpenAI SDK."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.input_schema,
                },
            }
            for t in self.tools
        ]
