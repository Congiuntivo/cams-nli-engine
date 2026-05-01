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
                                         dataset.py ──▶ compare_protocols() ──▶ ProtocolScore
```

## Module structure

| file            | responsibility                                                               |
| --------------- | ---------------------------------------------------------------------------- |
| `parser.py`     | JSONL → `SessionLog` / `TurnLog` / `ToolCallRecord` / `StepRecord`           |
| `metrics.py`    | `SessionLog` → `SessionMetrics` (frozen dataclass)                           |
| `comparison.py` | `compare_protocols(actual, expected)` → `ProtocolScore`                      |
| `dataset.py`    | Manifest loading (`load_manifest`) and batch evaluation (`evaluate_dataset`) |
| `report.py`     | Rich table rendering and `write_json_report`                                 |
| `cli.py`        | `nli-eval` entry point: `run` and `dataset` subcommands                      |

## CLI

```
nli-eval run     <LOG>      [--output PATH]
nli-eval dataset <MANIFEST> [--output PATH]
```

`--output` writes full results as JSON; omitting it prints only the Rich table.

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
    prompt: "record steps with the smartphone, heartbeat every hour"
    expected: cases/001_expected.json
    log: runs/001.jsonl
  - id: "002_complex_study"
    prompt: "EMA three times a day, GPS background tracking"
    expected: cases/002_expected.json
    log: runs/002.jsonl
```

Required fields: `id`, `prompt`, `expected`, `log`. The `prompt` field is
metadata — the evaluator does not use it to run the engine.

## Comparison model

`compare_protocols(actual, expected, value_comparator=None)` flattens both dicts
into `{dotted.key.path: leaf_value}` maps (lists are indexed numerically, e.g.
`tasks.0.name`) and computes:

| score                    | meaning                                                             |
| ------------------------ | ------------------------------------------------------------------- |
| `key_recall`             | fraction of expected leaf keys present in actual (coverage)         |
| `key_precision`          | fraction of actual leaf keys present in expected (no hallucination) |
| `exact_value_match_rate` | for shared keys, fraction with identical values                     |
| `smart_value_score`      | optional; populated by `value_comparator` if provided               |

`value_comparator` is the extension point for semantic comparison. Its signature
is `(key_path: str, actual_val: Any, expected_val: Any) -> float` returning a
score in `[0.0, 1.0]`. Pass a custom comparator to plug in normalised string
matching, embeddings, or an LLM-as-judge without changing any other code.
