"""Build the long per-field-per-case CSV consumed by ``fig:eval-perfield-case-gpt54``.

Joins ``study/preprocessed/hashmatch_fields.csv`` with
``study/preprocessed/sessions.csv`` on ``session_id`` and emits one row per
(session, field) contributing to the grouped-bar plot for the headline model
``gpt-5.4``. Sessions with ``workflow_complete == False`` do not appear in
``hashmatch_fields.csv``, so the join naturally selects completed runs.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[2]
FIELDS_CSV = Path(__file__).parent / "hashmatch_fields.csv"
SESSIONS_CSV = Path(__file__).parent / "sessions.csv"
OUTPUT = Path(__file__).parent / "eval_perfield_case_gpt54_long.csv"

MODEL = "gpt-5.4"
CASE_IDS = {"001_diary_study", "002_diary_study", "003_cardio_wellness"}
FIELDS = {
    "primaryDevices",
    "connectedDevices",
    "tasks",
    "triggers",
    "taskControls",
    "connections",
    "applicationData",
    "other",
}


def main() -> int:
    """Emit the long CSV; return 0 on success and non-zero on failure."""
    with SESSIONS_CSV.open() as fh:
        session_meta: dict[str, dict[str, str]] = {}
        for row in csv.DictReader(fh):
            if row["source"] != "models":
                continue
            if row["model"] != MODEL:
                continue
            if row["case_id"] not in CASE_IDS:
                continue
            session_meta[row["session_id"]] = {
                "case_id": row["case_id"],
                "prompt_key": row["prompt_key"],
                "run": row["run"],
            }

    out_rows: list[dict[str, str]] = []
    seen_sessions: set[str] = set()
    with FIELDS_CSV.open() as fh:
        for row in csv.DictReader(fh):
            if row["source"] != "models":
                continue
            sid = row["session_id"]
            meta = session_meta.get(sid)
            if meta is None:
                continue
            if row["field_name"] not in FIELDS:
                continue
            f1 = row["f1"].strip()
            if not f1:
                continue
            out_rows.append(
                {
                    "session_id": sid,
                    "case_id": meta["case_id"],
                    "prompt_key": meta["prompt_key"],
                    "run": meta["run"],
                    "field_name": row["field_name"],
                    "f1": f1,
                }
            )
            seen_sessions.add(sid)

    fieldnames = ["session_id", "case_id", "prompt_key", "run", "field_name", "f1"]
    with OUTPUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(
        f"wrote {OUTPUT.resolve().relative_to(ROOT)} "
        f"({len(out_rows)} rows across {len(seen_sessions)} sessions x 8 fields)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
