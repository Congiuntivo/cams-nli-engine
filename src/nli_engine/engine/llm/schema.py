from nli_engine.engine.tools import BoundTool


def bound_tool_to_schema(tool: BoundTool) -> dict:
    """Convert a BoundTool to an OpenAI function-calling schema dict.

    Mutation tools derive their parameters object from
    ``request_model.model_json_schema()``. Read-only tools (no request_model)
    receive an empty parameters schema so the LLM can still invoke them by name.

    Args:
        tool: The bound tool to convert.

    Returns:
        OpenAI-format tool schema with ``type``, ``function.name``,
        ``function.description``, and ``function.parameters``.
    """
    if tool.request_model is None:
        parameters: dict = {"type": "object", "properties": {}}
    else:
        parameters = tool.request_model.model_json_schema()
        parameters.pop("title", None)

    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": parameters,
        },
    }
