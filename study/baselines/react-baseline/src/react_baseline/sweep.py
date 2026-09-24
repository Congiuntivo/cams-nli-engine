"""Sweep driver CLI: iterate over (case, prompt_variant, run) cells."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import httpx
import yaml
from dotenv import load_dotenv

from react_baseline.agent import run_cell
from react_baseline.logger import SessionLogger
from react_baseline.mcp_bridge import McpBridge
from react_baseline.system_prompt import render as render_system_prompt

_MODEL = "gpt-5.4"
_WORKFLOW = "react_baseline"
_TURN_CAP = 30
_TEMPERATURE = 0.0
_SEED: int | None = 42
_PROMPT_KEYS = ("poor", "medium", "rich")
_RUNS_PER_CELL = 3

_CARP_MCP_BINARY_DEFAULT = "/home/simone/carp/cams_server/mcp_server/.venv/bin/carp-mcp"
_RETRIEVAL_MCP_BINARY_DEFAULT = (
    "/home/simone/carp/nli_engine/study/baselines/react-baseline"
    "/.venv/bin/react-baseline-retrieval-mcp"
)


def main() -> None:
    """Entry point for the ``react-baseline-sweep`` script."""
    load_dotenv()
    args = _parse_args()

    manifest_path = Path(args.manifest)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cases = _load_manifest(manifest_path)
    cells = _resolve_cells(cases, args)
    if not cells:
        print("No matching cells.", file=sys.stderr)
        sys.exit(1)

    print(f"Running {len(cells)} cell(s).")
    asyncio.run(
        _run_sweep(
            cells=cells,
            output_dir=output_dir,
            carp_base_url=os.environ.get("CARP_API_BASE_URL", "http://localhost:8080"),
            carp_mcp_binary=args.carp_mcp_binary,
            retrieval_mcp_binary=args.retrieval_mcp_binary,
        )
    )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run the ReAct baseline sweep.")
    p.add_argument(
        "--manifest",
        default=os.environ.get(
            "MANIFEST_PATH", "/home/simone/carp/nli_engine/dataset/manifest.yaml"
        ),
    )
    p.add_argument(
        "--output-dir",
        default=os.environ.get(
            "OUTPUT_DIR",
            "/home/simone/carp/nli_engine/study/baselines/react-baseline/results",
        ),
    )
    p.add_argument(
        "--carp-mcp-binary",
        default=os.environ.get("CARP_MCP_BINARY", _CARP_MCP_BINARY_DEFAULT),
    )
    p.add_argument(
        "--retrieval-mcp-binary",
        default=os.environ.get("RETRIEVAL_MCP_BINARY", _RETRIEVAL_MCP_BINARY_DEFAULT),
    )
    p.add_argument("--case", help="Filter to one case id (e.g. 001_diary_study).")
    p.add_argument("--prompt", choices=_PROMPT_KEYS, help="Filter to one prompt key.")
    p.add_argument("--run", type=int, help="Filter to one run number (1-based).")
    p.add_argument(
        "--runs-per-cell",
        type=int,
        default=_RUNS_PER_CELL,
        help="Runs per (case, prompt) cell.",
    )
    return p.parse_args()


def _load_manifest(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text())
    return list(data.get("cases", []))


def _resolve_cells(
    cases: list[dict[str, Any]],
    args: argparse.Namespace,
) -> list[tuple[str, str, int, str]]:
    """Expand the grid, applying any --case / --prompt / --run filters.

    Returns:
        List of ``(case_id, prompt_key, run_number, prompt_text)`` tuples.
    """
    runs = [args.run] if args.run else list(range(1, args.runs_per_cell + 1))

    cells: list[tuple[str, str, int, str]] = []
    for case in cases:
        case_id = case["id"]
        if args.case and case_id != args.case:
            continue
        prompts = case.get("prompts", {})
        for prompt_key in _PROMPT_KEYS:
            if args.prompt and prompt_key != args.prompt:
                continue
            if prompt_key not in prompts:
                continue
            for run in runs:
                cells.append((case_id, prompt_key, run, prompts[prompt_key]))
    return cells


async def _run_sweep(
    *,
    cells: list[tuple[str, str, int, str]],
    output_dir: Path,
    carp_base_url: str,
    carp_mcp_binary: str,
    retrieval_mcp_binary: str,
) -> None:
    bridge = McpBridge(
        carp_mcp_binary=carp_mcp_binary,
        retrieval_mcp_binary=retrieval_mcp_binary,
    )

    async def body(bridge: McpBridge) -> None:
        async with httpx.AsyncClient(base_url=carp_base_url, timeout=60.0) as http:
            for case_id, prompt_key, run, prompt_text in cells:
                protocol_name = _protocol_name(case_id, prompt_key, run)
                log_path = output_dir / f"{protocol_name}.jsonl"
                print(f"→ {protocol_name}", flush=True)

                session_id = await _create_session(http, protocol_name)
                system_prompt = render_system_prompt(session_id=session_id)

                with SessionLogger(log_path) as logger:
                    logger.session_start(
                        workflow=_WORKFLOW, protocol_name=protocol_name
                    )
                    logger.user_turn(prompt_text)

                    result = await run_cell(
                        user_prompt=prompt_text,
                        system_prompt=system_prompt,
                        model=_MODEL,
                        turn_cap=_TURN_CAP,
                        temperature=_TEMPERATURE,
                        seed=_SEED,
                        bridge=bridge,
                        logger=logger,
                    )

                    protocol = await _fetch_protocol(http, session_id)
                    done = result.serialized and protocol is not None

                    logger.turn_result(
                        response=result.final_text,
                        done=done,
                        protocol=protocol,
                        step_logs=[
                            {
                                "step_name": "baseline_agent",
                                "model": _MODEL,
                                "input_tokens": result.total_input_tokens,
                                "output_tokens": result.total_output_tokens,
                                "latency_ms": result.latency_ms,
                            }
                        ],
                    )

                print(
                    f"   turns={result.turns_used} "
                    f"llm_calls={result.n_llm_calls} "
                    f"serialized={result.serialized} "
                    f"done={done} "
                    f"in_tok={result.total_input_tokens} "
                    f"out_tok={result.total_output_tokens} "
                    f"latency_ms={result.latency_ms:.0f}",
                    flush=True,
                )

    await bridge.run(body)


def _protocol_name(case_id: str, prompt_key: str, run: int) -> str:
    return f"react-baseline_{_MODEL}_{case_id}_{prompt_key}_run{run:02d}"


async def _create_session(http: httpx.AsyncClient, name: str) -> str:
    response = await http.post("/sessions", json={"name": name})
    response.raise_for_status()
    return response.json()["sessionId"]


async def _fetch_protocol(
    http: httpx.AsyncClient, session_id: str
) -> dict[str, Any] | None:
    """Return the serialized protocol, or None if critical requirements remain."""
    response = await http.get(f"/sessions/{session_id}/serialize")
    if response.status_code == 409:
        return None
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    main()
