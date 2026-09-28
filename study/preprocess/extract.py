"""Extract per-source JSONL logs into flat table rows.

The public entry point is :func:`process_source`, which walks one
:class:`~study.preprocess.sources.Source` and returns five row lists plus a
mapping of ``session_id -> unwrapped actual protocol`` suitable for
per-session JSON dumps.

Each row list is designed to become a single DataFrame with a ``source`` and
``session_id`` column, so the four sources can be concatenated downstream.

The heavy lifting (event parsing, metric aggregation, HashMatch) is delegated
to :mod:`nli_engine.eval`; this module only adds:

* re-reading raw JSONL to capture per-step ``extra`` payloads (retrieval
  telemetry) and per-tool ``arguments`` / ``result_len`` that the typed
  parser discards.
* source-specific protocol unwrapping (see :func:`normalize.unwrap_protocol`).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from nli_engine.eval.io.dataset import DatasetCase
from nli_engine.eval.io.parser import parse_session
from nli_engine.eval.scoring.hashmatch import HashMatchScore
from nli_engine.eval.scoring.metrics import compute_metrics

from .normalize import protocol_sizes, synthetic_react_workflow_config, unwrap_protocol
from .sources import Source


def process_source(
    source: Source,
    cases_by_id: dict[str, DatasetCase],
    expected_cache: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Preprocess every JSONL under ``source.results_dir``.

    Args:
        source: The corpus to process.
        cases_by_id: Manifest cases keyed by case_id (from ``load_manifest``).
        expected_cache: Optional cross-source cache of loaded expected
            protocols keyed by ``case_id``. Passed in so multiple sources
            share one cache during a notebook run.

    Returns:
        Dict with keys ``sessions``, ``steps``, ``tools``, ``hashmatch_fields``,
        ``workflow_configs`` (each a list of row dicts), ``protocols`` (a
        ``session_id -> protocol dict`` mapping), and ``skipped`` (a list of
        ``(filename, reason)`` tuples for logs the extractor couldn't handle).
    """
    if expected_cache is None:
        expected_cache = {}

    out: dict[str, Any] = {
        "sessions": [],
        "steps": [],
        "tools": [],
        "hashmatch_fields": [],
        "workflow_configs": [],
        "protocols": {},
        "skipped": [],
    }

    if not source.results_dir.exists():
        out["skipped"].append((str(source.results_dir), "results_dir missing"))
        return out

    for log_path in sorted(source.results_dir.glob("*.jsonl")):
        try:
            _process_one(log_path, source, cases_by_id, expected_cache, out)
        except Exception as exc:  # noqa: BLE001 — surface everything to caller
            out["skipped"].append((log_path.name, f"{type(exc).__name__}: {exc}"))

    return out


def _process_one(
    log_path: Path,
    source: Source,
    cases_by_id: dict[str, DatasetCase],
    expected_cache: dict[str, dict[str, Any]],
    out: dict[str, Any],
) -> None:
    match = source.filename_regex.match(log_path.stem)
    if match is None:
        out["skipped"].append((log_path.name, "filename regex mismatch"))
        return

    model = match["model"]
    case_id = match["case_id"]
    prompt_key = match["prompt"]
    run = int(match["run"])
    session_id = log_path.stem

    case = cases_by_id.get(case_id)
    if case is None:
        out["skipped"].append((log_path.name, f"case {case_id!r} not in manifest"))
        return

    session = parse_session(log_path)
    metrics = compute_metrics(session)

    actual_protocol = unwrap_protocol(
        session.turns[-1].protocol if session.turns else None,
        react_style=source.react_style_protocol,
    )
    out["protocols"][session_id] = actual_protocol

    hashmatch: HashMatchScore | None = None
    if actual_protocol is not None:
        if case_id not in expected_cache:
            with case.expected_path.open() as fh:
                expected_cache[case_id] = json.load(fh)
        try:
            hashmatch = HashMatchScore.compute(actual_protocol, expected_cache[case_id])
        except (ValueError, KeyError) as exc:
            out["skipped"].append((log_path.name, f"hashmatch failed: {exc}"))

    step_extras, tool_details = _read_raw_extras(log_path)
    workflow_config = _read_workflow_config(log_path)
    if workflow_config is None and source.react_style_protocol:
        workflow_config = synthetic_react_workflow_config(model)

    base_ids = {
        "source": source.name,
        "session_id": session_id,
        "model": model,
        "case_id": case_id,
        "prompt_key": prompt_key,
        "run": run,
    }

    response_text = session.turns[-1].response if session.turns else ""
    session_row: dict[str, Any] = {
        **base_ids,
        "workflow": session.workflow,
        "protocol_name": session.protocol_name,
        "ts_start": session.ts_start.isoformat(),
        "ts_end": session.ts_end.isoformat() if session.ts_end else None,
        "workflow_complete": metrics.workflow_complete,
        "has_protocol": actual_protocol is not None,
        "n_turns": metrics.n_turns,
        "n_llm_calls": metrics.n_llm_calls,
        "n_tool_rounds": metrics.n_tool_rounds,
        "n_tool_calls": metrics.n_tool_calls,
        "n_failed_tool_calls": metrics.n_failed_tool_calls,
        "tool_failure_rate": metrics.tool_failure_rate,
        "n_unique_tools": metrics.n_unique_tools,
        "unique_tools_json": json.dumps(sorted(metrics.unique_tools_used)),
        "total_input_tokens": metrics.total_input_tokens,
        "total_output_tokens": metrics.total_output_tokens,
        "total_latency_ms": metrics.total_latency_ms,
        "response_len_chars": len(response_text),
        "response_text": response_text,
        "hm_f1": hashmatch.f1 if hashmatch else None,
        "hm_precision": hashmatch.precision if hashmatch else None,
        "hm_recall": hashmatch.recall if hashmatch else None,
        **protocol_sizes(actual_protocol),
    }
    out["sessions"].append(session_row)

    all_steps = [
        (t_idx, sr) for t_idx, t in enumerate(session.turns) for sr in t.step_logs
    ]
    for step_idx, (turn_idx, step) in enumerate(all_steps):
        extra = step_extras.get(step_idx, {}) or {}
        step_row: dict[str, Any] = {
            "source": source.name,
            "session_id": session_id,
            "turn_index": turn_idx,
            "step_index": step_idx,
            "step_name": step.step_name,
            "model": step.model,
            "input_tokens": step.input_tokens,
            "output_tokens": step.output_tokens,
            "latency_ms": step.latency_ms,
            "retrieval_query": extra.get("query"),
            "retrieval_n_chunks": extra.get("n_chunks"),
            "retrieval_chunks_json": (
                json.dumps(extra["chunks"]) if extra.get("chunks") is not None else None
            ),
            "extra_json": json.dumps(extra) if extra else None,
        }
        out["steps"].append(step_row)

    all_tool_calls = [
        (t_idx, tc) for t_idx, t in enumerate(session.turns) for tc in t.tool_calls
    ]
    for global_idx, (turn_idx, tc) in enumerate(all_tool_calls):
        detail = tool_details[global_idx] if global_idx < len(tool_details) else {}
        tool_row: dict[str, Any] = {
            "source": source.name,
            "session_id": session_id,
            "turn_index": turn_idx,
            "tool_call_index": global_idx,
            "ts": tc.ts.isoformat(),
            "tool_name": tc.tool_name,
            "is_error": tc.is_error,
            "arguments_json": detail.get("arguments_json"),
            "result_len": detail.get("result_len"),
        }
        out["tools"].append(tool_row)

    if hashmatch is not None:
        for field_name, fs in hashmatch.per_field.items():
            field_row = {
                "source": source.name,
                "session_id": session_id,
                "field_name": field_name,
                **asdict(fs),
            }
            out["hashmatch_fields"].append(field_row)

    if workflow_config is not None:
        cfg = workflow_config.get("config", {}) or {}
        retrieval = cfg.get("retrieval", {}) or {}
        out["workflow_configs"].append(
            {
                "source": source.name,
                "session_id": session_id,
                "default_model": (cfg.get("models") or {}).get("default"),
                "retrieval_method": retrieval.get("method"),
                "retrieval_rerank": retrieval.get("rerank"),
                "retrieval_top_k": retrieval.get("top_k"),
                "retrieval_prefetch_limit": retrieval.get("prefetch_limit"),
                "retrieval_min_score": retrieval.get("min_score"),
                "dense_model": retrieval.get("dense_model"),
                "sparse_model": retrieval.get("sparse_model"),
                "multi_model": retrieval.get("multi_model"),
                "temperatures_json": json.dumps(cfg.get("temperatures") or {}),
                "parameters_json": json.dumps(cfg.get("parameters") or {}),
                "max_iterations_json": json.dumps(cfg.get("max_iterations") or {}),
                "nli_engine_git_hash": workflow_config.get("nli_engine_git_hash"),
                "config_json": json.dumps(cfg),
            }
        )


def _read_raw_extras(
    path: Path,
) -> tuple[dict[int, dict[str, Any]], list[dict[str, Any]]]:
    """Return per-step ``extra`` payloads and per-tool-call detail rows.

    Args:
        path: The JSONL log to re-scan.

    Returns:
        A tuple ``(step_extras, tool_details)``. ``step_extras`` maps global
        step index → the ``extra`` dict from ``turn_result.logs``.
        ``tool_details`` is aligned to the flattened per-turn ``tool_call``
        sequence and holds ``arguments_json`` and ``result_len`` extracted
        from ``llm_tool_round.tool_calls``.
    """
    step_extras: dict[int, dict[str, Any]] = {}
    tool_details: list[dict[str, Any]] = []
    tool_call_count = 0
    pending: list[int] = []
    global_step_idx = 0

    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            kind = event.get("event")

            if kind == "tool_call":
                tool_details.append({"arguments_json": None, "result_len": None})
                pending.append(tool_call_count)
                tool_call_count += 1

            elif kind == "llm_tool_round":
                for tc in event.get("tool_calls", []) or []:
                    if not pending:
                        break
                    idx = pending.pop(0)
                    tool_details[idx] = {
                        "arguments_json": json.dumps(tc.get("arguments")),
                        "result_len": len(str(tc.get("result", ""))),
                    }

            elif kind == "turn_result":
                for log_entry in event.get("logs", []) or []:
                    extra = log_entry.get("extra") or {}
                    if extra:
                        step_extras[global_step_idx] = extra
                    global_step_idx += 1

    return step_extras, tool_details


def _read_workflow_config(path: Path) -> dict[str, Any] | None:
    """Return the first ``workflow_config`` event in the log, if any."""
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            if event.get("event") == "workflow_config":
                return event
    return None
