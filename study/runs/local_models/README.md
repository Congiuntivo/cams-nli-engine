In this study, for each configuration file in this folder, the engine is run against every case in the dataset manifest, once for each of that case's three prompts: `poor`, `medium`, and `rich`. Logs are written to `results/` with filename `<config_name>_<case_id>_<prompt_name>_run<NN>.jsonl` (two-digit, zero-padded run index).

All configs target local models hosted by Ollama at `http://localhost:11434`. The `ollama_chat/` LiteLLM prefix is used (not plain `ollama/`) so the workflow's tool calls hit Ollama's `/api/chat` endpoint, which supports native function calling.

Run the matrix with:

```bash
uv run python study/runs/local_models/run_study.py            # 1 run per (config, case, prompt)
uv run python study/runs/local_models/run_study.py --runs 3   # 3 runs per (config, case, prompt)
```

The runner is resumable: it counts existing `*_run*.jsonl` files for each (config, case, prompt) triple and only fills the gap up to `--runs`. Adding a new `*.yaml` config later runs only its missing combinations on the next invocation.

Requires:

- The CARP authoring server reachable at `http://localhost:8080`.
- Ollama reachable at `http://localhost:11434` with the model in each config's `models.default` already pulled (`docker exec ollama ollama list` to check).
