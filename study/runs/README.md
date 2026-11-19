# Study results

Per-run JSONL logs (`study/runs/**/results/`, `study/baselines/**/results/`) and the derived preprocessing artefacts (`study/preprocessed/steps.csv`, `study/preprocessed/tools.csv`, `study/preprocessed/protocols/`) are **not** tracked in git because their total size (~1.6 GB) exceeds what we want in the repo.

They are published as a GitHub Release asset: `nli_engine-study-results.tar.zst`.

## Download and extract

```bash
# Replace <TAG> with the release tag
curl -L -o nli_engine-study-results.tar.zst \
  https://github.com/<owner>/<repo>/releases/download/<TAG>/nli_engine-study-results.tar.zst

sha256sum -c <<<"9f1e06aeceb6bf7039c35e8d85cd51c7fb3496e6918825b959544099ab32d2bc  nli_engine-study-results.tar.zst"

tar --zstd -xf nli_engine-study-results.tar.zst
```

The archive extracts directly into the repo tree, so run it from the repo root. Contents:

- `study/runs/models/results/` (cloud models)
- `study/runs/norag/results/` (noRAG ablation)
- `study/runs/local_models/results/` (local models)
- `study/baselines/react-baseline/results/` (ReAct baseline)
- `study/preprocessed/steps.csv`, `tools.csv`, `protocols/`

Checksum: `9f1e06aeceb6bf7039c35e8d85cd51c7fb3496e6918825b959544099ab32d2bc` (sha256).

## Reproducing

To regenerate the artefacts from scratch, see the `run_study.py` scripts under each `study/runs/*/` directory, and `study/preprocessed/build_*.py` for the preprocessing stage.
