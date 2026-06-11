# Eval

## Concept

`nli-eval` is a standalone evaluation tool that reads session logs produced by
`nli-engine --log-file` and computes metrics. It never starts a server or runs
the engine — it only reads existing `.jsonl` files.

Two modes:

- **Single run** — one log file in, one metrics report out.
- **Dataset** — a YAML manifest maps many log files to ground-truth protocol
  JSONs; the tool evaluates all cases and produces a per-case summary.

```
logs.jsonl ──▶ parser.py ──▶ SessionLog ──▶ metrics.py ──▶ SessionMetrics ──▶ report.py ──▶ stdout
                                                  │
                                         dataset.py ──▶ compare_protocols() ──▶ ComparisonResult
                                                              │
                                                    hashmatch.py ──▶ HashMatchScore (per-field F1)
```

## Module structure

```
eval/
  cli.py                    nli-eval entry point — argument parsing and dispatch only
  commands/
    run.py                  handler for the run subcommand
    dataset.py              handler for the dataset subcommand
    extract.py              handler for the extract subcommand
    canonicalize.py         handler for the canonicalize subcommand
  scoring/
    hashmatch.py            content-addressed set F1 → HashMatchScore (see hashmatch.md)
    comparison.py           compare_protocols(actual, expected) → ComparisonResult
    metrics.py              SessionLog → SessionMetrics (frozen dataclass)
  io/
    parser.py               JSONL → SessionLog / TurnLog / ToolCallRecord / StepRecord
    dataset.py              manifest loading (load_manifest) and batch evaluation
    report.py               Rich table rendering and write_json_report
```

## CLI

```
nli-eval run         <LOG>                     [--output PATH]
nli-eval dataset     <MANIFEST> [LOG]          [--output PATH] [--last-from LOGS_DIR]
nli-eval extract     <LOG>                     <OUTPUT>
nli-eval canonicalize <FILE> [<FILE>]          [--output PATH] [--out-dir DIR]
```

`--output` (on `run` / `dataset`) writes full results as JSON; omitting it prints only the Rich table.

`extract` writes the final protocol from the log as pretty-printed JSON to `OUTPUT`. It picks the
last turn that contains a non-null protocol, so a failed final turn does not discard an earlier
successful one. Exits with an error if no protocol is found.

`canonicalize` converts one or two protocols to the content-addressed form used internally by
HashMatch, for diffing. Each `FILE` can be a `.json` protocol or a `.jsonl` session log (the
final protocol is extracted automatically). One-file mode writes to stdout or `--output`; two-file
mode writes both outputs to `--out-dir` (defaults to `.`) named after the input files.

Passing a `LOG` path evaluates exactly one case: the manifest is searched for a
`(case_id, prompt_key)` pair whose prompt text matches the first `user_turn` in
the given log. Errors if no match is found.

`--last-from LOGS_DIR` scans all `*.jsonl` files in `LOGS_DIR` and, for each
`(case, prompt_key)` pair in the manifest, picks the most recently modified file
whose first `user_turn` text matches the prompt exactly. This lets you evaluate a
fresh batch of engine runs without touching the manifest:

```bash
uv run nli-engine --workflow one_shot_llm --name s1 \
  --prompt "record steps with smartphone" --log-file logs/run1.jsonl
uv run nli-eval dataset dataset/manifest.yaml --last-from logs/
```

Unmatched `(case_id, prompt_key)` pairs are skipped with a warning. Exactly one
of `LOG` or `--last-from` must be provided.

## JSONL parsing

`parse_session(path)` reads a `.jsonl` file line-by-line and groups events into
turns. A turn opens on `user_turn` and closes on `turn_result`. Events between
those two boundaries (`tool_call`, `llm_call`, `llm_tool_round`) are accumulated
on the open `TurnLog`.

```
SessionLog
├── workflow: str
├── protocol_name: str
├── ts_start: datetime          # from session_start
├── ts_end: datetime | None     # from last turn_result
└── turns: list[TurnLog]
    ├── user_text: str
    ├── tool_calls: list[ToolCallRecord]   # tool_name, is_error, ts
    ├── n_llm_rounds: int                  # llm_tool_round events
    ├── n_llm_calls: int                   # llm_call events
    ├── step_logs: list[StepRecord]        # from turn_result.logs
    ├── response: str
    ├── done: bool
    └── protocol: dict | None
```

`StepRecord` fields (`step_name`, `model`, `input_tokens`, `output_tokens`,
`latency_ms`) are populated from the `logs` array in the `turn_result` event.
That field was added in the same commit as this module — logs produced before
that point have an empty `step_logs` list and will show zero for token counts.

## Metrics reference

`compute_metrics(session)` returns a frozen `SessionMetrics`:

| metric                | source                                   | note                       |
| --------------------- | ---------------------------------------- | -------------------------- |
| `n_turns`             | count of `user_turn` events              |                            |
| `n_llm_calls`         | count of `llm_call` events               |                            |
| `n_tool_rounds`       | count of `llm_tool_round` events         |                            |
| `n_tool_calls`        | count of `tool_call` events              |                            |
| `n_failed_tool_calls` | `tool_call` events where `is_error=True` |                            |
| `tool_failure_rate`   | `n_failed / n_tool_calls`                | 0.0 when no tools called   |
| `unique_tools_used`   | distinct `tool_name` values              | `frozenset[str]`           |
| `n_unique_tools`      | cardinality of `unique_tools_used`       |                            |
| `total_input_tokens`  | sum of `StepRecord.input_tokens`         |                            |
| `total_output_tokens` | sum of `StepRecord.output_tokens`        |                            |
| `total_latency_ms`    | `ts_end - ts_start` in milliseconds      | 0.0 when no completed turn |
| `workflow_complete`   | `done` field of the last `turn_result`   |                            |

## Dataset manifest

Paths are resolved relative to the manifest file itself so that the manifest
directory is self-contained and portable.

```yaml
# dataset/manifest.yaml
cases:
  - id: "001_diary_study"
    expected: cases/001_expected.json
    prompts:
      v1: "record steps with the smartphone, heartbeat every hour"
      detailed: "record steps and location every hour..."
  - id: "002_complex_study"
    expected: cases/002_expected.json
    prompts:
      v1: "EMA three times a day, GPS background tracking"
```

Required fields: `id`, `prompts` (non-empty mapping of prompt_key → prompt text),
`expected`. Multiple prompts per case represent different "richness" levels that
should all produce the same gold-standard protocol. Log resolution happens at CLI
invocation time — the manifest carries no log paths.

## Comparison model

`compare_protocols(actual, expected)` returns a `ComparisonResult` containing a
`HashMatchScore`. The score is computed by `HashMatchScore.compute`, which:

1. Converts both protocols to content-addressed form (arrays become hash-keyed
   dicts, cross-references are rewritten to stable content hashes).
2. Decomposes each protocol into named categories (`primaryDevices`, `tasks`,
   `triggers`, `connections`, `taskControls`, `dataEndpoint`, and an `other`
   bucket for remaining top-level keys).
3. Computes set F1 (TP / FP / FN over content-hash sets) for each category.
4. Macro-averages F1, precision, and recall across categories.

This approach follows the component-wise F1 design from Yu et al. (2018) Spider.
See [hashmatch.md](hashmatch.md) for the full algorithm and design rationale.
