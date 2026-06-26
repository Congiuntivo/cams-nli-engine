In this study, for each configuration file in this folder, the engine is run against case `003_cardio_wellness` once for each of its three prompts: `poor`, `medium`, and `rich`. Logs are written to `results/` with filename `<config_name>_<prompt_name>_run<NN>.jsonl` (two-digit, zero-padded run index).

Run the matrix with:

```bash
uv run python study/runs/models/run_study.py            # 1 run per (config, prompt)
uv run python study/runs/models/run_study.py --runs 3   # 3 runs per (config, prompt)
```

The runner is resumable: it counts existing `*_run*.jsonl` files for each pair and only fills the gap up to `--runs`. Adding a new `*.yaml` config later runs only its missing combinations on the next invocation.

Requires the CARP authoring server to be reachable at `http://localhost:8080`.
