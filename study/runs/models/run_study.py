"""Batch runner for the model-comparison study.

For every ``*.yaml`` config in this directory, every case in the dataset
manifest, and every prompt richness variant of that case, invoke
``nli-engine`` once and dump its JSONL session log into ``results/``.

The runner is resumable: it skips (config, case, prompt) triples that
already have the requested number of logs. Bumping ``--runs`` only fills
in the gap.

Run from the repo root::

    uv run python study/runs/models/run_study.py            # 1 run / triple
    uv run python study/runs/models/run_study.py --runs 3   # 3 runs / triple

Log filename convention: ``<config>_<caseId>_<prompt>_run<NN>.jsonl``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from nli_engine.eval import load_manifest

CONFIGS_DIR = Path(__file__).resolve().parent
RESULTS_DIR = CONFIGS_DIR / "results"
REPO_ROOT = CONFIGS_DIR.parents[2]
MANIFEST_PATH = REPO_ROOT / "dataset" / "manifest.yaml"


def log_path_for(
    config_stem: str, case_id: str, prompt_key: str, run_number: int
) -> Path:
    """Return the log path for a (config, case, prompt, run) tuple."""
    return (
        RESULTS_DIR / f"{config_stem}_{case_id}_{prompt_key}_run{run_number:02d}.jsonl"
    )


def existing_run_count(config_stem: str, case_id: str, prompt_key: str) -> int:
    """Count logs already on disk for this (config, case, prompt) triple."""
    return len(
        list(RESULTS_DIR.glob(f"{config_stem}_{case_id}_{prompt_key}_run*.jsonl"))
    )


def invoke_engine(
    config_path: Path,
    case_id: str,
    prompt_key: str,
    prompt_text: str,
    run_number: int,
) -> int:
    """Run ``nli-engine`` once and return its exit code."""
    log_path = log_path_for(config_path.stem, case_id, prompt_key, run_number)
    name = f"{config_path.stem}_{case_id}_{prompt_key}_run{run_number:02d}"
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
    if not cases:
        sys.exit(f"No cases found in {MANIFEST_PATH}")

    configs = sorted(CONFIGS_DIR.glob("*.yaml"))
    if not configs:
        sys.exit(f"No YAML config files found in {CONFIGS_DIR}")

    planned = 0
    succeeded = 0
    failed: list[str] = []

    try:
        for config in configs:
            for case in cases:
                for prompt_key, prompt_text in case.prompts.items():
                    existing = existing_run_count(config.stem, case.id, prompt_key)
                    needed = max(0, args.runs - existing)
                    if needed == 0:
                        print(
                            f"[skip] {config.stem} / {case.id} / {prompt_key}: "
                            f"{existing} run(s) already present",
                            flush=True,
                        )
                        continue
                    for offset in range(needed):
                        run_number = existing + offset + 1
                        planned += 1
                        rc = invoke_engine(
                            config, case.id, prompt_key, prompt_text, run_number
                        )
                        if rc == 0:
                            succeeded += 1
                        elif rc == 130:
                            # Child received SIGINT — the user is stopping the whole
                            # sweep, not just this cell. Bail out cleanly.
                            print(
                                "\nInterrupted; stopping sweep.",
                                file=sys.stderr,
                                flush=True,
                            )
                            return 130
                        else:
                            failed.append(
                                f"{config.stem}/{case.id}/{prompt_key}/"
                                f"run{run_number:02d} (exit {rc})"
                            )
                            print(
                                f"[fail] exit code {rc}",
                                file=sys.stderr,
                                flush=True,
                            )
    except KeyboardInterrupt:
        print("\nInterrupted; stopping sweep.", file=sys.stderr, flush=True)
        return 130

    print(f"\nDone. {succeeded}/{planned} runs succeeded.")
    if failed:
        print("Failed runs:", file=sys.stderr)
        for name in failed:
            print(f"  - {name}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
