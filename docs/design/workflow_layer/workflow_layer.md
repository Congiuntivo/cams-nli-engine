# Workflow layer

![Workflow layer diagram](workflow_layer.png)

## Concept

The workflow layer sits above the session layer. Its job is to:

- Orchestrate a sequence of **Steps** against a `ProtocolSession` to satisfy a user request.
- Maintain full conversation state in a `WorkflowContext` passed across every step and turn.
- Keep structure separate from parameters: a workflow encodes _what runs and in what order_; `WorkflowConfig` encodes _which models and settings_ to use.
- Return a typed `TurnResult` per turn — carrying the human message, step logs, assembled protocol, and a `done` flag.
- Record a `StepLog` for every step so callers (CLI, GUI) have structured observability without touching step internals.

```mermaid
flowchart LR
    U([User]) --> C["Conversation.turn()"]
    C --> W["Workflow.run_turn()"]
    W --> S["Step₁ … Stepₙ"]
    S --> PS["ProtocolSession.tools()"]
    PS --> LS["LLM + Server"]
    W -. "WorkflowContext
    flows through every step" .-> S
    W --> TR(["TurnResult"])
    TR --> UI["CLI / GUI"]
```

The workflow itself signals completion via `TurnResult.done`. When `done=True`, the caller must not invoke `run_turn()` again.

## Components

### `engine/workflow/config.py`

`WorkflowConfig` is a Pydantic model loaded from a YAML file. It carries one model ID per named step and an open `parameters` dict for anything else. Each concrete `Workflow` subclass validates that the keys it requires are present at construction time, before any LLM call fires.

```yaml
# Example workflow.yaml
models:
  refiner: claude-haiku-4-5-20251001
  orchestrator: claude-sonnet-4-6
  specialist: claude-sonnet-4-6
parameters:
  api_base: "https://api.openai.com/v1/"
```

### `engine/workflow/log.py`

`StepLog` is a frozen Pydantic model. Every `Step.run()` call must produce one regardless of step type.

| field           | type             | meaning                                     |
| --------------- | ---------------- | ------------------------------------------- |
| `step_name`     | `str`            | identifies the step                         |
| `model`         | `str \| None`    | model used; `None` for non-LLM steps        |
| `input_tokens`  | `int`            | 0 for non-LLM steps                         |
| `output_tokens` | `int`            | 0 for non-LLM steps                         |
| `latency_ms`    | `float`          | wall-clock duration of the step             |
| `extra`         | `dict[str, Any]` | step-specific metadata (e.g. RAG hit count) |

### `engine/workflow/result.py`

`TurnResult` is the typed return value of every `run_turn()` call. It cleanly separates human-readable output from machine-readable state.

| field      | type            | meaning                                              |
| ---------- | --------------- | ---------------------------------------------------- |
| `message`  | `str`           | human-readable text (LLM reply or generated summary) |
| `logs`     | `list[StepLog]` | per-step observability                               |
| `done`     | `bool`          | `True` → caller must not call `run_turn()` again     |
| `protocol` | `dict \| None`  | serialized protocol if available, `None` otherwise   |

### `engine/workflow/base.py`

Four abstractions live here.

**`Message`** — one message in LLM API format.

| field          | type                                   | meaning                                                         |
| -------------- | -------------------------------------- | --------------------------------------------------------------- |
| `role`         | `Literal["user", "assistant", "tool"]` |                                                                 |
| `content`      | `str \| list \| None`                  | `None` for assistant turns that contain only tool calls         |
| `tool_calls`   | `list[dict] \| None`                   | set on assistant turns with tool calls; `None` otherwise        |
| `tool_call_id` | `str \| None`                          | set on tool-result turns; matches the originating `ToolCall.id` |

**`WorkflowContext`** — abstract Pydantic model; the shared mutable state. Never instantiated directly. Every concrete workflow defines its own subclass and adds the fields its steps need (e.g. `retrieved_chunks: list[str]` for a RAG workflow). The base carries only `history`.

| field     | type            | meaning                                         |
| --------- | --------------- | ----------------------------------------------- |
| `history` | `list[Message]` | full conversation history, never truncated here |

**`Step`** — abstract base for all step types. Steps receive the full context and only the tools they declared. Non-LLM steps (retrieval, formatting, validation, …) subclass `Step` directly. `LLMStep` (see below) is one concrete specialisation — there is no intermediate `DeterministicStep` base because it would add no shared behaviour.

| member                | type        | meaning                                         |
| --------------------- | ----------- | ----------------------------------------------- |
| `name`                | `str`       | unique within a workflow                        |
| `tool_names`          | `list[str]` | tools this step may call; empty list = no tools |
| `run(context, tools)` | abstract    | returns `(output, StepLog)`                     |

**`Workflow[C]`** — abstract base, generic over `C` (bound to `WorkflowContext`). The type parameter lets each concrete workflow declare its own context type in the signature of `run_turn`, so subclasses never need to cast.

| member                             | type                   | meaning                                   |
| ---------------------------------- | ---------------------- | ----------------------------------------- |
| `config`                           | `WorkflowConfig`       | validated at construction                 |
| `_all_tools`                       | `dict[str, BoundTool]` | all tools from the session, keyed by name |
| `run_turn(user_input, context: C)` | abstract               | returns `TurnResult`                      |
| `_resolve_tools(step)`             | protected              | filters `_all_tools` by `step.tool_names` |

### `engine/workflow/registry.py`

`WorkflowSpec` (frozen dataclass) describes one registered workflow. `WORKFLOW_REGISTRY` maps IDs to specs — the single source of truth consumed by the CLI selector, the GUI picker, and `Conversation`.

| field            | type                    | meaning                            |
| ---------------- | ----------------------- | ---------------------------------- |
| `id`             | `str`                   | stable identifier, e.g. `"dummy"`  |
| `name`           | `str`                   | human display name                 |
| `description`    | `str`                   | one-line description for selectors |
| `workflow_class` | `type[Workflow]`        | concrete workflow to instantiate   |
| `context_class`  | `type[WorkflowContext]` | matching context to instantiate    |

### `engine/conversation.py`

`Conversation` is the GUI-agnostic driver shared by both the CLI and the GUI. It holds a concrete `Workflow` and its `WorkflowContext` for the lifetime of one user session.

```python
class Conversation:
    def __init__(self, spec: WorkflowSpec, config: WorkflowConfig, session: ProtocolSession) -> None: ...
    def turn(self, user_input: str) -> TurnResult: ...
```

Neither the CLI nor the GUI ever touches `Workflow` or `WorkflowContext` directly — they go through `Conversation`.

### `engine/workflow/steps/`

| file     | class     | role                                                                                                                                           |
| -------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `llm.py` | `LLMStep` | subclasses `Step`; runs the agentic loop — calls `LLMClient.complete()`, dispatches tool calls, repeats until the LLM produces a text response |

`LLMStep` constructor parameters:

| parameter        | type        | meaning                                            |
| ---------------- | ----------- | -------------------------------------------------- |
| `name`           | `str`       | step name (appears in `StepLog`)                   |
| `tool_names`     | `list[str]` | tools this step may call                           |
| `client`         | `LLMClient` | configured transport (model + optional `api_base`) |
| `system_prompt`  | `str`       | system message prepended before history            |
| `max_iterations` | `int`       | safety limit on tool-call rounds (default: 10)     |

See the [LLM layer design](../llm_layer/llm_layer.md) for `LLMClient`, schema conversion, and tool dispatch.

### `engine/workflow/specialist.py`

Provides the three building blocks for the orchestrator/specialist multi-agent pattern.

**`SpecialistContext`** — a concrete, minimal `WorkflowContext` subclass with no extra
fields. Used to give each specialist an isolated history containing only the delegation
instruction; the main conversation history is never exposed to a specialist.

**`DelegationRequest`** — a single-field Pydantic model used as the `request_model` for
every delegation `BoundTool`:

| field         | type  | meaning                                                                                                     |
| ------------- | ----- | ----------------------------------------------------------------------------------------------------------- |
| `instruction` | `str` | natural-language instruction from the orchestrator, including all names and parameters the specialist needs |

**`build_specialist_tool(name, description, step, domain_tools) → BoundTool`** — wraps
an `LLMStep` as a `BoundTool` so the orchestrator can call it via standard tool
calling. When invoked, it:

1. Creates a fresh `SpecialistContext`.
2. Appends the `DelegationRequest.instruction` as the single user message.
3. Runs `step.run(context, domain_tools)`.
4. Returns the specialist's final text reply as the tool result content.

Because `DelegationRequest` satisfies the `BoundTool.request_model` contract, the
existing `call_tool()` dispatch and `bound_tool_to_schema()` schema generation work
without modification. Injecting the returned `BoundTool` into `Workflow._all_tools`
lets `_resolve_tools()` resolve it for the orchestrator step like any other tool.

### `engine/workflow/workflows/`

| file              | class                | behaviour                                                                                                              |
| ----------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `dummy.py`        | `DummyWorkflow`      | deterministic baseline — hard-codes the three tool calls; no LLM involved                                              |
| `dummy_llm.py`    | `DummyLLMWorkflow`   | LLM-driven version — instructs the model to call the same three tools via `LLMStep`                                    |
| `one_shot_llm.py` | `OneShotLLMWorkflow` | production workflow — refiner → planner → orchestrator with domain specialists; see [one_shot_llm.md](one_shot_llm.md) |

## Step hierarchy

```mermaid
flowchart TD
    S["Step (abstract)"]
    L["LLMStep
    calls an LLM · agentic tool-call loop"]
    R["RAGStep
    retrieval · subclasses Step directly"]
    X["… any other deterministic step"]
    S --> L
    S --> R
    S --> X
```

## Tool visibility

Every workflow holds all tools from the session. Each step receives only the subset it declared by name.

```mermaid
flowchart TD
    SES["session.tools()"]
    AT["Workflow._all_tools
    dict keyed by name"]
    A["Step A
    tool_names=[add_task]"]
    B["Step B
    tool_names=[]"]
    SES --> AT
    AT --> A
    AT --> B
```

## Workflow usage

```python
config  = WorkflowConfig.from_yaml("workflow.yaml")
session = ProtocolSession(build_client(), name="My Study")
spec    = WORKFLOW_REGISTRY["my_workflow"]

conversation = Conversation(spec, config, session)
while True:
    user_input = input("> ")
    result = conversation.turn(user_input)
    print(result.message)
    if result.done:
        break
```
