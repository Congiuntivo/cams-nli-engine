"""Build the wide per-field, per-model F1 CSV consumed by ``tab:eval-perfield-tier``.

Joins ``study/preprocessed/hashmatch_fields.csv`` against ``sessions.csv`` on
``session_id`` (restricted to ``source == "models"``) and aggregates per-field
F1 scores into one row per HashMatch field, with a column per cloud model, plus
the minimum contributing-session count across the row for caption input.
"""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[2]
SESSIONS = Path(__file__).parent / "sessions.csv"
FIELDS = Path(__file__).parent / "hashmatch_fields.csv"
OUTPUT = Path(__file__).parent / "eval_perfield_tier_wide.csv"

CLOUD_MODELS = [
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5.4-nano",
    "gpt-5-nano",
    "gpt-4o-mini",
]

FIELD_ORDER = [
    "primaryDevices",
    "connectedDevices",
    "tasks",
    "triggers",
    "taskControls",
    "connections",
    "applicationData",
    "other",
]


def main() -> int:
    with SESSIONS.open() as fh:
        session_model: dict[str, str] = {
            r["session_id"]: r["model"]
            for r in csv.DictReader(fh)
            if r["source"] == "models" and r["model"] in CLOUD_MODELS
        }

    cells: dict[tuple[str, str], list[float]] = {}
    with FIELDS.open() as fh:
        for r in csv.DictReader(fh):
            if r["source"] != "models":
                continue
            model = session_model.get(r["session_id"])
            if model is None:
                continue
            field = r["field_name"]
            if field not in FIELD_ORDER:
                continue
            raw = r["f1"].strip()
            if not raw:
                continue
            cells.setdefault((model, field), []).append(float(raw))

    rows: list[dict[str, str]] = []
    cells_populated = 0
    global_min_sessions = None
    for field in FIELD_ORDER:
        row: dict[str, str] = {"field": field}
        session_counts: list[int] = []
        for model in CLOUD_MODELS:
            values = cells.get((model, field), [])
            session_counts.append(len(values))
            if values:
                row[model] = repr(statistics.fmean(values))
                cells_populated += 1
            else:
                row[model] = ""
                print(
                    f"warning: no completing sessions for ({model}, {field}); "
                    "cell left empty.",
                    file=sys.stderr,
                )
        row_min = min(session_counts)
        row["n_sessions_min"] = str(row_min)
        global_min_sessions = (
            row_min
            if global_min_sessions is None
            else min(global_min_sessions, row_min)
        )
        rows.append(row)

    fieldnames = ["field", *CLOUD_MODELS, "n_sessions_min"]
    with OUTPUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(
        f"wrote {OUTPUT.resolve().relative_to(ROOT)} "
        f"({len(rows)} fields, {cells_populated} cells populated, "
        f"min_sessions_per_cell={global_min_sessions})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
