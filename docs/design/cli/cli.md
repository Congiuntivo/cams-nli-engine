# CLI

## Concept

The CLI is a thin I/O wrapper around the engine layer. It owns no conversation logic — that lives in `engine/conversation.py` (`Conversation`) and `engine/workflow/registry.py` (`WORKFLOW_REGISTRY`), which the GUI reuses without modification.

```
nli-engine (argparse)
    └── cli/args.py          parse args, dispatch
        └── cli/interactive.py   Rich prompts + display loop
            └── engine/conversation.py   Conversation.turn()
```

## Module structure

| file                 | responsibility                                                           |
| -------------------- | ------------------------------------------------------------------------ |
| `cli/__init__.py`    | Single `main()` that calls `args.run()`. Never grows.                    |
| `cli/args.py`        | `argparse` setup, all flag definitions, dispatch to mode handlers.       |
| `cli/interactive.py` | Rich-powered interactive session: workflow selector, turn loop, display. |

## Arguments

```
nli-engine [--workflow ID] [--mode {interactive,non-interactive}]
           [--server URL] [--config PATH]
```

| flag         | default                    | meaning                                          |
| ------------ | -------------------------- | ------------------------------------------------ |
| `--mode`     | `interactive`              | `non-interactive` raises `NotImplementedError`   |
| `--workflow` | _(prompt)_                 | skip the selector; use this registry ID directly |
| `--server`   | `http://localhost:8080`    | authoring server base URL                        |
| `--config`   | _(empty `WorkflowConfig`)_ | path to a workflow YAML config file              |

All future argument growth (new modes, subcommands, output flags) lands in `args.py`. The entrypoint `cli/__init__.py` is stable.

## Interactive session flow

```
1. Workflow selection
   ├── --workflow given → validate ID against WORKFLOW_REGISTRY, use it
   └── else → display rich.Table of registered workflows; Prompt.ask to pick

2. Protocol name
   └── Prompt.ask("Protocol name") → passed to ProtocolSession

3. Session bootstrap
   └── build_client(server) → ProtocolSession(client, name) → Conversation(spec, config, session)

4. Turn loop
   ├── Prompt.ask for user input
   ├── "exit" / "quit" / Ctrl-C → clean exit
   ├── conversation.turn(input) → TurnResult
   ├── display result.message in Panel
   ├── display result.protocol in Panel (if present)
   ├── display step logs in Table
   └── result.done=True → print "Workflow complete." and exit
```

## Rich components

| component    | used for                                      |
| ------------ | --------------------------------------------- |
| `Console`    | all output; module-level singleton            |
| `Table`      | workflow selector, step log display           |
| `Panel`      | assistant message and serialized protocol     |
| `Prompt.ask` | workflow selection, protocol name, user input |

## Installation

```bash
uv sync --extra cli
uv run nli-engine
```
