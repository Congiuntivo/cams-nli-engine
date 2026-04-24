# NLI Engine

Natural-language interface engine for authoring CARP study protocols.

## Architecture

```mermaid
flowchart LR
    User(["User"])
    CLIGUI["CLI / GUI"]
    WF["Workflow Layer"]
    SL["Session Layer"]
    GC["Generated Client"]
    PS[["Protocol Server\n:8080"]]

    User --> CLIGUI --> WF --> SL --> GC --> PS
```

The engine receives free-text descriptions of a study protocol, maps them to API
calls via an LLM planner, and assembles the protocol on a running authoring server.

**Key principle:** `session_id` is managed entirely by the engine — the LLM never
sees it. Every API operation is exposed as a `BoundTool` with `session_id`
pre-filled and a pydantic schema the LLM can use for structured output.

## Usage

```bash
# Install with CLI support
uv sync --extra cli

# Interactive session (prompts for workflow and protocol name)
uv run nli-engine

# Skip the workflow selector
uv run nli-engine --workflow dummy

# Custom server or config
uv run nli-engine --server http://my-server:8080 --config workflow.yaml
```

Type `exit` or press `Ctrl-C` to quit an interactive session.

## Design docs

- [Session layer](docs/design/session_layer/session_layer.md) — how `ProtocolSession`, `ToolSpec`, and `BoundTool` fit together ([diagram](docs/design/session_layer/session_layer.puml))
- [Workflow layer](docs/design/workflow_layer/workflow_layer.md) — how `Workflow`, `Step`, `WorkflowContext`, `TurnResult`, and `Conversation` fit together ([diagram](docs/design/workflow_layer/workflow_layer.puml))
- [CLI](docs/design/cli/cli.md) — argument structure, interactive flow, and Rich component map

## Development

```bash
uv sync --all-extras
uv run pytest
```
