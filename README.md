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

### Install with CLI extras

```bash
uv sync --extra cli
```

### Basic interactive session

```bash
uv run nli-engine
```

### Run with configuration file

```bash
uv run nli-engine --config workflow.yaml
```

### Fully automated run with no prompts

```bash
uv run nli-engine \
  --workflow one_shot_llm \
  --name "my-study" \
  --prompt "record steps with the smartphone, heartbeat every hour" \
  --config workflow.yaml \
  --log-file run.jsonl
```

Type `exit` or press `Ctrl-C` to quit an interactive session.

### Flags reference

| Flag              | Default                 | Description                                                                                        |
| ----------------- | ----------------------- | -------------------------------------------------------------------------------------------------- |
| `--workflow ID`   | —                       | Skip the workflow selector and use this workflow directly                                          |
| `--name NAME`     | —                       | Protocol name; skips the interactive name prompt                                                   |
| `--prompt TEXT`   | —                       | Fire the first turn automatically; best combined with `--workflow` and `--name`                    |
| `--config PATH`   | —                       | Path to a workflow YAML config file                                                                |
| `--server URL`    | `http://localhost:8080` | Authoring server base URL                                                                          |
| `--log-file PATH` | —                       | Write a full JSON Lines session log (see [CLI design doc](docs/design/cli/cli.md#session-logging)) |
| `-v` / `-vv`      | —                       | Verbose trace: `-v` one-line events, `-vv` full debug blocks                                       |

### Workflow config

LLM workflows require a YAML config file that maps step names to model identifiers
and provides provider-specific parameters:

```yaml
# workflow.yaml
models:
  default: "ollama/qwen2.5:7b" # or "gpt-4o", "anthropic/claude-sonnet-4-6", …
  # override individual steps (all fall back to "default" if omitted):
  # orchestrator: "gpt-4o"
parameters:
  api_base: "http://localhost:11434" # required for Ollama; omit for cloud providers
```

Model identifiers follow [LiteLLM's routing conventions](https://docs.litellm.ai/docs/providers).

### Available workflows

| ID             | Description                                                                                               |
| -------------- | --------------------------------------------------------------------------------------------------------- |
| `dummy`        | Deterministic baseline — hard-codes the three setup tool calls; no LLM                                    |
| `dummy_llm`    | LLM-driven version — instructs the model to make the same calls autonomously                              |
| `one_shot_llm` | Five-step pipeline: refiner → planner → extractor → setup → per-unit orchestrator with domain specialists |

## Evaluation

`nli-eval` reads session logs produced by `--log-file` and reports execution metrics.
No running engine or server required.

### Install with CLI extras

As with the engine, the evaluation CLI is included in the `cli` extra:

```bash
uv sync --extra cli
```

### Evaluate a single run

```bash
uv run nli-eval run run.jsonl
uv run nli-eval run run.jsonl --output metrics.json
```

### Evaluate a dataset

Provide a YAML manifest that describes the dataset — expected outputs and the
prompts that should produce them:

```yaml
# dataset/manifest.yaml
cases:
  - id: "001_diary_study"
    expected: cases/001_expected.json # relative to this file
    prompts:
      v1: "record steps with the smartphone, heartbeat every hour"
      detailed: "record steps and location every hour, collect participant name at enrolment"
```

The manifest has no log paths. Logs are resolved at evaluation time in one of two ways:

**Single log** — evaluate exactly one case by passing a log path. The manifest is
searched for a `(case_id, prompt_key)` pair whose prompt text matches the first
`user_turn` in the log:

```bash
uv run nli-eval dataset dataset/manifest.yaml logs/run1.jsonl
```

**Batch (`--last-from`)** — for each `(case, prompt_key)` pair in the manifest,
find the most recently modified `.jsonl` file in the given directory whose
`user_turn` matches the prompt text. Unmatched pairs are skipped with a warning:

```bash
uv run nli-eval dataset dataset/manifest.yaml --last-from logs/
uv run nli-eval dataset dataset/manifest.yaml --last-from logs/ --output results.json
```

### Extract the final protocol from a log

```bash
uv run nli-eval extract run.jsonl protocol.json
```

Writes the protocol from the last completed turn to `protocol.json`. Useful for
inspecting what the engine actually produced or seeding a new expected-output file.

### Inspect canonicalized protocol JSON

`canonicalize` converts one or two protocols to their content-addressed form — the
same internal representation used by HashMatch — so you can diff them directly:

```bash
# Single file → stdout
uv run nli-eval canonicalize dataset/cases/002_expected.json | jq .

# Single file → output file
uv run nli-eval canonicalize protocol.json --output ca.json

# Two files → both written to a directory, ready to diff
uv run nli-eval canonicalize run.jsonl dataset/cases/002_expected.json --out-dir /tmp/diff/
diff /tmp/diff/run.json /tmp/diff/002_expected.json
```

A `.jsonl` input is treated as a session log and the final protocol is extracted
automatically (same as `extract`).

See [eval design doc](docs/design/eval/eval.md) for the full metric reference and comparison model.

## Study data

Study run artefacts (per-run JSONL logs under `study/runs/**/results/` and `study/baselines/**/results/`, plus the preprocessing derivatives `study/preprocessed/steps.csv`, `tools.csv` and `protocols/`) are not tracked in git. They are published as a GitHub Release asset:

**[Study data v1 — nli_engine-study-results.tar.zst](https://github.com/Congiuntivo/cams-nli-engine/releases/tag/study-data-v1)** (~23 MB compressed, ~1.6 GB extracted).

Extract from the repo root so paths line up:

```bash
# From the repo root:
curl -L -o nli_engine-study-results.tar.zst \
  https://github.com/Congiuntivo/cams-nli-engine/releases/download/study-data-v1/nli_engine-study-results.tar.zst

sha256sum -c <<<"9f1e06aeceb6bf7039c35e8d85cd51c7fb3496e6918825b959544099ab32d2bc  nli_engine-study-results.tar.zst"

tar --zstd -xf nli_engine-study-results.tar.zst
rm nli_engine-study-results.tar.zst
```

See [`study/runs/README.md`](study/runs/README.md) for the archive layout and how to regenerate the artefacts.

## Design docs

- [Session layer](docs/design/session_layer/session_layer.md) — `ProtocolSession`, `ToolSpec`, `BoundTool` ([diagram](docs/design/session_layer/session_layer.puml))
- [Workflow layer](docs/design/workflow_layer/workflow_layer.md) — `Workflow`, `Step`, `WorkflowContext`, `TurnResult`, `Conversation` ([diagram](docs/design/workflow_layer/workflow_layer.puml))
- [LLM layer](docs/design/llm_layer/llm_layer.md) — `LLMClient`, `LLMStep`, schema conversion, tool dispatch ([diagram](docs/design/llm_layer/llm_layer.puml))
- [Retrieval layer](docs/design/retrieval_layer/retrieval_layer.md) — `Retriever`, `Document`, `RetrievedChunk`, `QueryExtractor`; backends: `KeywordRetriever` (in-memory), `QdrantRetriever` (hybrid dense+sparse+ColBERT); wired per-step via `LLMStep(retriever=…)`
- [CLI](docs/design/cli/cli.md) — argument structure, interactive flow, Rich components, session logging
- [Eval](docs/design/eval/eval.md) — `nli-eval` CLI, JSONL parsing, metrics, dataset manifest, comparison model

## Development

```bash
uv sync --all-extras
uv run pytest
```

### Regenerate the API client

The generated client under `src/nli_engine/client/_generated/` is produced from
`openapi/openapi.yaml`. Regenerate it after changing the spec (requires Java):

```bash
bash openapi/generate_client.sh
```

The generated code is committed to the repo so CI and fresh clones work without Java.

### First-time Qdrant setup

Set `FASTEMBED_CACHE_PATH`, `QDRANT_URL`, and `QDRANT_COLLECTION` in `.env`, then download the FastEmbed models once:

```bash
uv run python scripts/download_models.py
```

The script exits with an error if `FASTEMBED_CACHE_PATH` is unset. Models are downloaded only on the first run; subsequent calls are instant.
