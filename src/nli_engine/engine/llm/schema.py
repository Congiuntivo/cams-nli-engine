from nli_engine.engine.tools import BoundTool


def bound_tool_to_schema(tool: BoundTool) -> dict:
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
