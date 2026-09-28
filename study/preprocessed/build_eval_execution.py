"""Build the wide CSV consumed by ``tab:eval-execution``.

Reads ``study/preprocessed/sessions.csv``, filters to the pipeline cloud-model
population (``source == "models"`` and ``model`` in the five thesis cloud
models), aggregates per ``(model, case)`` over the nine (3 richness x 3 run)
sessions per cell, and writes a wide long-format CSV with mean/sd pairs for
five execution metrics: LLM calls, tool calls, tool-failure rate, input tokens
(millions), and latency (seconds).
"""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[2]
SESSIONS = Path(__file__).parent / "sessions.csv"
OUT = Path(__file__).parent / "eval_execution_wide.csv"

CASE_DISPLAY = {
    "001_diary_study": "Case 001",
    "002_diary_study": "Case 002",
    "003_cardio_wellness": "Case 003",
}
MODELS = ["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano", "gpt-5-nano", "gpt-4o-mini"]

METRICS: list[tuple[str, str, float]] = [
    ("llm_calls", "n_llm_calls", 1.0),
    ("tool_calls", "n_tool_calls", 1.0),
    ("tool_fail", "tool_failure_rate", 1.0),
    ("input_tokens", "total_input_tokens", 1_000_000.0),
    ("latency", "total_latency_ms", 1_000.0),
]


def _load_rows() -> list[dict]:
    with SESSIONS.open() as fh:
        rows = list(csv.DictReader(fh))
    return [r for r in rows if r["source"] == "models" and r["model"] in MODELS]


def _values(rows: list[dict], field: str, divisor: float) -> list[float]:
    out: list[float] = []
    for r in rows:
        raw = r[field].strip()
        if not raw:
            continue
        out.append(float(raw) / divisor)
    return out


def main() -> int:
    rows = _load_rows()

    fieldnames = ["case", "model"]
    for prefix, _, _ in METRICS:
        fieldnames.append(f"{prefix}_mean")
        fieldnames.append(f"{prefix}_sd")

    out_rows: list[dict[str, str]] = []
    for case_id, case_label in CASE_DISPLAY.items():
        for model in MODELS:
            cell_rows = [
                r for r in rows if r["case_id"] == case_id and r["model"] == model
            ]
            row: dict[str, str] = {"case": case_label, "model": model}
            for prefix, field, divisor in METRICS:
                values = _values(cell_rows, field, divisor)
                if not values:
                    row[f"{prefix}_mean"] = ""
                    row[f"{prefix}_sd"] = ""
                    continue
                row[f"{prefix}_mean"] = repr(statistics.fmean(values))
                row[f"{prefix}_sd"] = repr(statistics.pstdev(values))
            out_rows.append(row)

    with OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(
        f"wrote {OUT.resolve().relative_to(ROOT)} "
        f"({len(MODELS)} models x {len(CASE_DISPLAY)} cases)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
