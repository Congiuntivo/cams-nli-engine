"""Build the wide per-model evaluation-quality CSV consumed by ``tab:eval-quality``.

Reads ``study/preprocessed/sessions.csv`` and aggregates per-run ``hm_f1`` scores
into one row per frontier model, with a column per (case, prompt-richness) cell,
plus an unweighted grid-cell mean and the minimum contributing-run count.
"""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SESSIONS = Path(__file__).parent / "sessions.csv"
OUTPUT = Path(__file__).parent / "eval_quality_wide.csv"

FRONTIER_MODELS = [
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5.4-nano",
    "gpt-5-nano",
    "gpt-4o-mini",
]

CASE_KEYS = {
    "001_diary_study": "c1",
    "002_diary_study": "c2",
    "003_cardio_wellness": "c3",
}
PROMPT_KEYS = ["poor", "medium", "rich"]


def main() -> int:
    with SESSIONS.open() as fh:
        reader = csv.DictReader(fh)
        sessions = [r for r in reader if r["source"] == "models"]

    cells: dict[tuple[str, str, str], list[float]] = {}
    for r in sessions:
        model = r["model"]
        if model not in FRONTIER_MODELS:
            continue
        case_id = r["case_id"]
        if case_id not in CASE_KEYS:
            continue
        prompt = r["prompt_key"]
        if prompt not in PROMPT_KEYS:
            continue
        raw = r["hm_f1"].strip()
        if not raw:
            continue
        cells.setdefault((model, case_id, prompt), []).append(float(raw))

    rows: list[dict[str, str]] = []
    cells_populated = 0
    global_min_runs = 3
    for model in FRONTIER_MODELS:
        row: dict[str, str] = {"model": model}
        cell_values: list[float] = []
        missing: list[str] = []
        run_counts: list[int] = []
        for case_id, ckey in CASE_KEYS.items():
            for prompt in PROMPT_KEYS:
                col = f"{ckey}_{prompt}"
                values = cells.get((model, case_id, prompt), [])
                run_counts.append(len(values))
                if values:
                    mean = statistics.fmean(values)
                    row[col] = repr(mean)
                    cell_values.append(mean)
                    cells_populated += 1
                else:
                    row[col] = ""
                    missing.append(col)
        if len(cell_values) >= 5:
            row["model_mean"] = repr(statistics.fmean(cell_values))
        else:
            row["model_mean"] = ""
            print(
                f"warning: {model} has only {len(cell_values)}/9 cells populated; "
                f"missing={missing}. model_mean left empty.",
                file=sys.stderr,
            )
        row["n_runs_min"] = str(min(run_counts))
        global_min_runs = min(global_min_runs, min(run_counts))
        rows.append(row)

    fieldnames = [
        "model",
        "c1_poor",
        "c1_medium",
        "c1_rich",
        "c2_poor",
        "c2_medium",
        "c2_rich",
        "c3_poor",
        "c3_medium",
        "c3_rich",
        "model_mean",
        "n_runs_min",
    ]
    with OUTPUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(
        f"wrote {OUTPUT.resolve().relative_to(ROOT)} "
        f"({len(rows)} models, {cells_populated} cells populated, "
        f"min_runs_per_cell={global_min_runs})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
