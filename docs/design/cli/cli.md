# CLI

## Concept

The CLI is a thin I/O wrapper around the engine layer. It owns no conversation
logic — that lives in `engine/conversation.py` and `engine/workflow/`, which the
GUI reuses without modification.

```
nli-engine (argparse)
    └── cli/args.py             parse args, dispatch
        └── cli/interactive.py  Rich prompts + display loop
            └── engine/conversation.py  Conversation.turn()
```

## Module structure

| file                      | responsibility                                                                   |
| ------------------------- | -------------------------------------------------------------------------------- |
| `cli/__init__.py`         | Single `main()` that calls `args.run()`. Never grows.                            |
| `cli/args.py`             | `argparse` setup, all flag definitions, dispatch to mode handlers.               |
| `cli/interactive.py`      | `InteractiveCLI` class: workflow selector, session setup, turn loop, display.    |
| `cli/logging/console.py`  | `TraceHandler`: renders structured log events to a Rich console.                 |
| `cli/logging/file.py`     | `FileTraceHandler`: serialises all events to a JSON Lines file.                  |
| `cli/logging/__init__.py` | Re-exports `TraceHandler`, `FileTraceHandler`, and both `configure_*` functions. |

## Arguments

```
nli-engine [--workflow ID] [--name NAME] [--prompt TEXT]
           [--config PATH] [--server URL] [--log-file PATH]
           [--mode {interactive,non-interactive}] [-v | -vv]
```

| flag         | default                    | meaning                                               |
| ------------ | -------------------------- | ----------------------------------------------------- |
| `--mode`     | `interactive`              | `non-interactive` raises `NotImplementedError`        |
| `--workflow` | _(prompt)_                 | skip the selector; use this registry ID directly      |
| `--name`     | _(prompt)_                 | protocol name; skips the interactive name prompt      |
| `--prompt`   | _(none)_                   | fire the first turn automatically before the loop     |
| `--server`   | `http://localhost:8080`    | authoring server base URL                             |
| `--config`   | _(empty `WorkflowConfig`)_ | path to a workflow YAML config file                   |
| `--log-file` | _(none)_                   | write a JSON Lines session log to this path           |
| `-v` / `-vv` | _(silent)_                 | verbose console trace: INFO one-liners / DEBUG blocks |

All future argument growth lands in `args.py`. The entrypoint `cli/__init__.py` is stable.

## Interactive session flow

```
1. Verbosity + file logging setup
   ├── -v / -vv → configure_verbose_logging(console, INFO | DEBUG)
   └── --log-file → configure_file_logging(path)

2. Workflow selection
   ├── --workflow given → validate ID against WORKFLOW_REGISTRY, use it
   └── else → display rich.Table of registered workflows; Prompt.ask to pick

3. Protocol name
   ├── --name given → use directly
   └── else → Prompt.ask("Protocol name")

4. Session bootstrap
   └── emit session_start · build_client(server) · ProtocolSession(client, name) · Conversation(spec, config, session)

5. Initial prompt (optional)
   └── --prompt given → print input, _execute_turn(), display result; exit if result.done

6. Turn loop
   ├── Prompt.ask for user input
   ├── "exit" / "quit" / Ctrl-C → clean exit
   ├── _execute_turn(conversation, input)
   │   ├── emit user_turn
   │   ├── conversation.turn(input) → TurnResult
   │   └── emit turn_result
   ├── display result.message in Panel
   ├── display result.protocol in Panel (if present)
   ├── display step logs in Table
   └── result.done=True → print "Workflow complete." and exit
```

## Rich components

| component    | used for                                          |
| ------------ | ------------------------------------------------- |
| `Console`    | all output; instance variable on `InteractiveCLI` |
| `Table`      | workflow selector, step log display               |
| `Panel`      | assistant message and serialised protocol         |
| `Prompt.ask` | workflow selection, protocol name, user input     |

## Session logging

When `--log-file PATH` is set, `configure_file_logging` attaches a
`FileTraceHandler` at `DEBUG` level to all three trace loggers
(`nli_engine.session`, `nli_engine.step`, `nli_engine.llm`). Every event is
written as a JSON object on its own line (JSON Lines / `.jsonl`), flushed
immediately so the file is valid even after a crash.

### Event reference

| event                     | logger               | key fields                                          |
| ------------------------- | -------------------- | --------------------------------------------------- |
| `session_start`           | `nli_engine.session` | `workflow`, `protocol_name`                         |
| `user_turn`               | `nli_engine.session` | `text`                                              |
| `turn_result`             | `nli_engine.session` | `response`, `protocol`, `done`                      |
| `step_begin` / `step_end` | `nli_engine.step`    | `step_name`                                         |
| `llm_call`                | `nli_engine.llm`     | `model`                                             |
| `llm_request`             | `nli_engine.llm`     | `model`, `messages`, `n_tools`                      |
| `tool_call`               | `nli_engine.llm`     | `tool_name`, `is_error`                             |
| `llm_tool_round`          | `nli_engine.llm`     | `tool_calls` (name / arguments / result / is_error) |
| `llm_text_response`       | `nli_engine.llm`     | `text`                                              |

Every object also carries a `ts` field (ISO-8601 UTC).

### Example `jq` queries

```bash
# Full LLM conversation for every request
jq 'select(.event == "llm_request") | .messages' run.jsonl

# All tool calls and whether they succeeded
jq 'select(.event == "tool_call") | {tool: .tool_name, failed: .is_error}' run.jsonl

# Final assembled protocol
jq 'select(.event == "turn_result") | .protocol' run.jsonl

# LLM response text
jq 'select(.event == "turn_result") | .response' run.jsonl
```
