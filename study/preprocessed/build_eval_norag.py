"""Build the wide CSVs consumed by ``tab:eval-norag-summary`` and ``tab:eval-norag-cells``.

Reads ``study/preprocessed/sessions.csv`` and produces two wide CSVs comparing
the with-RAG pipeline arm (``source == "models" AND model == "gpt-5.4"``)
against the no-RAG ablation arm (``source == "norag"``, all ``model ==
"gpt-5.4"``): a headline summary of macro-F1, input tokens, tool calls, and
LLM calls (one row per arm, mean/sd pairs across the 27 runs), and a per-cell
long-format CSV of the nine (case, richness) F1 means/sds partitioned across
three case sections at render time.
"""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[2]
SESSIONS = Path(__file__).parent / "sessions.csv"
SUMMARY_OUT = Path(__file__).parent / "eval_norag_summary_wide.csv"
CELLS_OUT = Path(__file__).parent / "eval_norag_cells_wide.csv"

CASE_DISPLAY = {
    "001_diary_study": "Case 001",
    "002_diary_study": "Case 002",
    "003_cardio_wellness": "Case 003",
}
PROMPT_KEYS = ["poor", "medium", "rich"]
ARMS = ["with_rag", "no_rag"]


def _hm_f1(row: dict) -> float:
    raw = row["hm_f1"].strip()
    return float(raw) if raw else 0.0


def _num(row: dict, col: str) -> float:
    raw = row[col].strip()
    return float(raw) if raw else 0.0


def _load_arms() -> dict[str, list[dict]]:
    with SESSIONS.open() as fh:
        rows = list(csv.DictReader(fh))
    return {
        "with_rag": [
            r for r in rows if r["source"] == "models" and r["model"] == "gpt-5.4"
        ],
        "no_rag": [r for r in rows if r["source"] == "norag"],
    }


def _write_summary(arms: dict[str, list[dict]]) -> None:
    fieldnames = ["arm"]
    for prefix in ("f1", "input_tokens", "tool_calls", "llm_calls"):
        fieldnames.append(f"{prefix}_mean")
        fieldnames.append(f"{prefix}_sd")

    rows_out: list[dict[str, str]] = []
    for arm in ARMS:
        sessions = arms[arm]
        f1 = [_hm_f1(r) for r in sessions]
        it = [_num(r, "total_input_tokens") / 1e6 for r in sessions]
        tc = [_num(r, "n_tool_calls") for r in sessions]
        lc = [_num(r, "n_llm_calls") for r in sessions]
        rows_out.append(
            {
                "arm": arm,
                "f1_mean": repr(statistics.fmean(f1)),
                "f1_sd": repr(statistics.pstdev(f1)),
                "input_tokens_mean": repr(statistics.fmean(it)),
                "input_tokens_sd": repr(statistics.pstdev(it)),
                "tool_calls_mean": repr(statistics.fmean(tc)),
                "tool_calls_sd": repr(statistics.pstdev(tc)),
                "llm_calls_mean": repr(statistics.fmean(lc)),
                "llm_calls_sd": repr(statistics.pstdev(lc)),
            }
        )

    with SUMMARY_OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)


def _cell_stats(rows: list[dict], case: str, prompt: str) -> tuple[str, str]:
    values = [
        _hm_f1(r) for r in rows if r["case_id"] == case and r["prompt_key"] == prompt
    ]
    if not values:
        return "", ""
    return repr(statistics.fmean(values)), repr(statistics.pstdev(values))


def _write_cells(arms: dict[str, list[dict]]) -> None:
    fieldnames = ["case", "arm"]
    for prompt in PROMPT_KEYS:
        fieldnames.append(f"{prompt}_mean")
        fieldnames.append(f"{prompt}_sd")

    rows_out: list[dict[str, str]] = []
    for case_id, case_label in CASE_DISPLAY.items():
        for arm in ARMS:
            row: dict[str, str] = {"case": case_label, "arm": arm}
            for prompt in PROMPT_KEYS:
                mean, sd = _cell_stats(arms[arm], case_id, prompt)
                row[f"{prompt}_mean"] = mean
                row[f"{prompt}_sd"] = sd
            rows_out.append(row)

    with CELLS_OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)


def main() -> int:
    arms = _load_arms()
    _write_summary(arms)
    _write_cells(arms)

    print(f"wrote {SUMMARY_OUT.resolve().relative_to(ROOT)} ({len(ARMS)} arms)")
    print(
        f"wrote {CELLS_OUT.resolve().relative_to(ROOT)} "
        f"({len(ARMS)} arms x {len(CASE_DISPLAY)} cases)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
