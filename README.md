# NLI Engine

Natural-language interface engine for authoring CARP study protocols.

## Architecture

```mermaid
flowchart LR
    User(["User"])
    CLIGUI["CLI / GUI"]
    WF["Workflow Layer"]
    LLM["LLM Layer"]
    SL["Session Layer"]
    GC["Generated Client"]
    PS[["Protocol Server\n:8080"]]

    User --> CLIGUI --> WF --> LLM --> SL --> GC --> PS
```

The engine receives free-text descriptions of a study protocol, maps them to API
calls via an LLM planner, and assembles the protocol on a running authoring server.

**Key principle:** `session_id` is managed entirely by the engine — the LLM never
sees it. Every API operation is exposed as a `BoundTool` with `session_id`
pre-filled and a Pydantic schema the LLM can use for structured output.

## Usage

```bash
# Install with CLI
uv sync --extra cli

# Interactive session (prompts for workflow and protocol name)
uv run nli-engine

# Skip the workflow selector
uv run nli-engine --workflow dummy_llm --config workflow.yaml

# Print live LLM trace (requests, tool calls, responses)
uv run nli-engine --workflow dummy_llm --config workflow.yaml --verbose

# Custom server
uv run nli-engine --server http://my-server:8080 --config workflow.yaml
```

Type `exit` or press `Ctrl-C` to quit an interactive session.

### Workflow config

LLM workflows require a YAML config file that maps step names to model identifiers
and provides provider-specific parameters:

```yaml
# workflow.yaml
models:
  planner: "ollama/qwen2.5:7b" # or "gpt-4o", "anthropic/claude-sonnet-4-6", …
parameters:
  api_base: "http://localhost:11434" # required for Ollama; omit for cloud providers
```

Model identifiers follow [LiteLLM's routing conventions](https://docs.litellm.ai/docs/providers).

### Available workflows

| ID          | Description                                                                  |
| ----------- | ---------------------------------------------------------------------------- |
| `dummy`     | Deterministic baseline — hard-codes the three setup tool calls; no LLM       |
| `dummy_llm` | LLM-driven version — instructs the model to make the same calls autonomously |

## Design docs

- [Session layer](docs/design/session_layer/session_layer.md) — `ProtocolSession`, `ToolSpec`, `BoundTool` ([diagram](docs/design/session_layer/session_layer.puml))
- [Workflow layer](docs/design/workflow_layer/workflow_layer.md) — `Workflow`, `Step`, `WorkflowContext`, `TurnResult`, `Conversation` ([diagram](docs/design/workflow_layer/workflow_layer.puml))
- [LLM layer](docs/design/llm_layer/llm_layer.md) — `LLMClient`, `LLMStep`, schema conversion, tool dispatch ([diagram](docs/design/llm_layer/llm_layer.puml))
- [CLI](docs/design/cli/cli.md) — argument structure, interactive flow, Rich component map

## Development

```bash
uv sync --all-extras
uv run pytest
```
