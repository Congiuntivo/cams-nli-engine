"""Batch runner for the model-comparison study.

For every ``*.yaml`` config in this directory and every prompt richness
variant of case ``003_cardio_wellness`` in the dataset manifest, invoke
``nli-engine`` once and dump its JSONL session log into ``results/``.

The runner is resumable: it skips (config, prompt) pairs that already
have the requested number of logs. Bumping ``--runs`` only fills in the
gap.

Run from the repo root::

    uv run python study/runs/models/run_study.py            # 1 run / pair
    uv run python study/runs/models/run_study.py --runs 3   # 3 runs / pair
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from nli_engine.eval import load_manifest

CASE_ID = "003_cardio_wellness"
CONFIGS_DIR = Path(__file__).resolve().parent
RESULTS_DIR = CONFIGS_DIR / "results"
REPO_ROOT = CONFIGS_DIR.parents[2]
MANIFEST_PATH = REPO_ROOT / "dataset" / "manifest.yaml"


def log_path_for(config_stem: str, prompt_key: str, run_number: int) -> Path:
    """Return the log path for a (config, prompt, run) triple."""
    return RESULTS_DIR / f"{config_stem}_{prompt_key}_run{run_number:02d}.log"


def existing_run_count(config_stem: str, prompt_key: str) -> int:
    """Count logs already on disk for this (config, prompt) pair."""
    return len(list(RESULTS_DIR.glob(f"{config_stem}_{prompt_key}_run*.log")))


def invoke_engine(
    config_path: Path, prompt_key: str, prompt_text: str, run_number: int
) -> int:
    """Run ``nli-engine`` once and return its exit code."""
    log_path = log_path_for(config_path.stem, prompt_key, run_number)
    name = f"{config_path.stem}_{prompt_key}_run{run_number:02d}"
    cmd = [
        "uv",
        "run",
        "nli-engine",
        "--workflow",
        "one_shot_llm",
        "--name",
        name,
        "--config",
        str(config_path),
        "--prompt",
        prompt_text,
        "--log-output",
        str(log_path),
    ]
    print(f">>> {name}", flush=True)
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Target number of runs per (config, prompt) pair (default: 1).",
    )
    args = parser.parse_args()

    if args.runs < 1:
        sys.exit("--runs must be >= 1")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    cases = load_manifest(MANIFEST_PATH)
    case = next((c for c in cases if c.id == CASE_ID), None)
    if case is None:
        sys.exit(f"Case {CASE_ID!r} not found in {MANIFEST_PATH}")

    configs = sorted(CONFIGS_DIR.glob("*.yaml"))
    if not configs:
        sys.exit(f"No YAML config files found in {CONFIGS_DIR}")

    planned = 0
    succeeded = 0
    failed: list[str] = []

    for config in configs:
        for prompt_key, prompt_text in case.prompts.items():
            existing = existing_run_count(config.stem, prompt_key)
            needed = max(0, args.runs - existing)
            if needed == 0:
                print(
                    f"[skip] {config.stem} / {prompt_key}: "
                    f"{existing} run(s) already present",
                    flush=True,
                )
                continue
            for offset in range(needed):
                run_number = existing + offset + 1
                planned += 1
                rc = invoke_engine(config, prompt_key, prompt_text, run_number)
                if rc == 0:
                    succeeded += 1
                else:
                    failed.append(
                        f"{config.stem}/{prompt_key}/run{run_number:02d} (exit {rc})"
                    )
                    print(f"[fail] exit code {rc}", file=sys.stderr, flush=True)

    print(f"\nDone. {succeeded}/{planned} runs succeeded.")
    if failed:
        print("Failed runs:", file=sys.stderr)
        for name in failed:
            print(f"  - {name}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
