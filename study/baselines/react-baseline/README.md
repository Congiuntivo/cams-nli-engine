# react-baseline

Generic ReAct-style tool-using agent baseline for CAMS study-protocol
generation. Drives `gpt-5.4` with MCP-exposed CAMS authoring operations and a
dense-only retrieval tool over the same Qdrant collection the NLI engine uses.

The whole point of the baseline is a _deliberately un-specialized_ agent — no
refiner, planner, orchestrator, or specialist decomposition. Just one LLM in a
loop with the same typed tools the pipeline uses.

## Prerequisites

1. **CAMS authoring server** running on `:8080` (defaults to
   `CARP_API_BASE_URL=http://localhost:8080`).
   ```bash
   docker run --rm -d --name cams-authoring-server \
       -p 8080:8080 ghcr.io/congiuntivo/cams-authoring-server:latest
   ```
2. **Qdrant** reachable at `QDRANT_URL`, with the collection populated by the
   NLI engine's kb pipeline (env: `QDRANT_COLLECTION`, default `carp-docs`).
3. **FastEmbed model cache** at `FASTEMBED_CACHE_PATH` — for the retrieval
   server. Same path the engine uses.
4. **Ollama** serving the dense embedder `mahonzhan/all-MiniLM-L6-v2` (LiteLLM
   calls it as `ollama/mahonzhan/all-MiniLM-L6-v2`).
5. **`OPENAI_API_KEY`** for `gpt-5.4`.

Copy `.env.example` to `.env` and fill in the values.

## Install

```bash
cd /home/simone/carp/nli_engine/study/baselines/react-baseline
uv sync
```

This installs the baseline package, the nli_engine editable dependency (for
the retriever), the MCP client SDK, and FastMCP (for the retrieval server).

## Run one cell (smoke test)

```bash
uv run react-baseline-sweep --case 001_diary_study --prompt medium --run 1
```

Result lands at
`results/react-baseline_gpt-5.4_001_diary_study_medium_run01.jsonl`.

Sanity-check with the engine's evaluator:

```bash
cd /home/simone/carp/nli_engine
uv run nli-eval extract \
    study/baselines/react-baseline/results/react-baseline_gpt-5.4_001_diary_study_medium_run01.jsonl \
    /tmp/baseline_protocol.json

uv run nli-eval aggregate \
    --manifest dataset/manifest.yaml \
    --base study/baselines \
    --csv /tmp/baseline_smoke.csv
```

The `source` column in the CSV will read `react-baseline`.

## Full sweep

```bash
uv run react-baseline-sweep --runs-per-cell 3
```

27 cells (3 cases × 3 prompts × 3 runs), serial. Configurable via CLI flags.

## Design notes

- **Session isolation.** Every cell mints a fresh CAMS authoring session via
  `POST /sessions`. The session id is pinned into the system prompt; the agent
  is told to include it on every CAMS tool call. `createProtocolSession` is
  explicitly forbidden in the prompt so the agent cannot double-create.
- **Same tool surface as the pipeline.** All 45 CAMS operations from
  `openapi/openapi.yaml` are exposed via the FastMCP sidecar plus one retrieval
  tool. No file-edit / shell / Python tools — deliberately.
- **Retrieval asymmetry.** The pipeline uses hybrid retrieval (BM25 + dense +
  ColBERT rerank, RRF fusion). The baseline uses **dense-only** via the same
  Qdrant collection and same embedder (`ollama/mahonzhan/all-MiniLM-L6-v2`).
  Accepted as a scope decision; see thesis limitations.
- **Termination.** The agent is instructed to call `serializeProtocol` when it
  believes the protocol is complete. After the loop, the sweep script re-fetches
  the protocol via `GET /sessions/{id}/serialize` — a `409` means critical
  requirements were unmet and `done` is emitted as `false`.
- **Determinism knobs.** `temperature=0`, `seed=42`. The `gpt-5.4` API accepts
  the seed but does not guarantee bit-exact reproducibility across capacity.
- **Log format.** Emits the JSONL schema consumed by `nli_engine.eval.io.parser`
  directly (no converter). Events: `session_start`, `user_turn`, `llm_call`,
  `llm_tool_round`, `tool_call`, `turn_result`.

## Files

```
src/react_baseline/
├── system_prompt.py    # renders template + CAMS_info + session id
├── retrieval_server.py # FastMCP stdio server exposing search_docs
├── mcp_bridge.py       # spawns and multiplexes both MCP servers
├── logger.py           # JSONL event writer matching nli-eval's schema
├── agent.py            # ReAct loop, turn cap 30, termination on serialize
└── sweep.py            # CLI driver: --case / --prompt / --run / --all
```
