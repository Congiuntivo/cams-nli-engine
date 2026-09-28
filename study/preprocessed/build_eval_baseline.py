"""Build the wide CSVs consumed by ``tab:eval-baseline-summary`` and ``tab:eval-baseline-cells``.

Reads ``study/preprocessed/sessions.csv`` and produces two wide CSVs comparing
the pipeline arm (``source == "models" AND model == "gpt-5.4"``) against the
ReAct generic-agent baseline (``source == "react_baseline"``): a transposed
summary of completion / quality / cost stats (one row per metric, one column
per arm), and a per-case long-format CSV of the nine (case, richness) F1
means/sds partitioned across three case sections at render time.
"""

from __future__ import annotations

import csv
import statistics
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[2]
SESSIONS = Path(__file__).parent / "sessions.csv"
SUMMARY_OUT = Path(__file__).parent / "eval_baseline_summary_wide.csv"
CELLS_OUT = Path(__file__).parent / "eval_baseline_cells_wide.csv"

CASE_DISPLAY = {
    "001_diary_study": "Case 001",
    "002_diary_study": "Case 002",
    "003_cardio_wellness": "Case 003",
}
PROMPT_KEYS = ["poor", "medium", "rich"]

ARMS = ["pipeline", "baseline"]


def _hm_f1(row: dict) -> float:
    raw = row["hm_f1"].strip()
    return float(raw) if raw else 0.0


def _num(row: dict, col: str) -> float:
    raw = row[col].strip()
    return float(raw) if raw else 0.0


def _fmt_paired(mean: float, sd: float, decimals: int) -> str:
    return f"${mean:.{decimals}f} \\pm {sd:.{decimals}f}$"


def _bold(s: str) -> str:
    return r"\bfseries " + s


def _load_arms() -> dict[str, list[dict]]:
    with SESSIONS.open() as fh:
        rows = list(csv.DictReader(fh))
    return {
        "pipeline": [
            r for r in rows if r["source"] == "models" and r["model"] == "gpt-5.4"
        ],
        "baseline": [r for r in rows if r["source"] == "react_baseline"],
    }


def _summary_row(
    metric: str,
    pipe_mean: float,
    pipe_sd: float,
    base_mean: float,
    base_sd: float,
    decimals: int,
    winner: str,
) -> dict[str, str]:
    """Format one summary metric row.

    Args:
        winner: ``"max"`` or ``"min"`` — direction of "better". Bolds the arm
            whose mean is strictly better; if the two means tie, neither is
            bolded. For ``"max"``, a mean of exactly ``0.0`` is never bolded.
    """
    pipe = _fmt_paired(pipe_mean, pipe_sd, decimals)
    base = _fmt_paired(base_mean, base_sd, decimals)
    if winner == "max" and max(pipe_mean, base_mean) > 0.0 and pipe_mean != base_mean:
        if pipe_mean > base_mean:
            pipe = _bold(pipe)
        else:
            base = _bold(base)
    elif winner == "min" and pipe_mean != base_mean:
        if pipe_mean < base_mean:
            pipe = _bold(pipe)
        else:
            base = _bold(base)
    return {"metric": metric, "pipeline": pipe, "baseline": base}


def _write_summary(arms: dict[str, list[dict]]) -> tuple[int, int]:
    pipe = arms["pipeline"]
    base = arms["baseline"]

    pipe_f1_all = [_hm_f1(r) for r in pipe]
    base_f1_all = [_hm_f1(r) for r in base]
    pipe_f1_nt = [v for v in pipe_f1_all if v > 0]
    base_f1_nt = [v for v in base_f1_all if v > 0]
    pipe_it = [_num(r, "total_input_tokens") for r in pipe]
    base_it = [_num(r, "total_input_tokens") for r in base]
    pipe_tc = [_num(r, "n_tool_calls") for r in pipe]
    base_tc = [_num(r, "n_tool_calls") for r in base]

    total = len(pipe)
    rows_out: list[dict[str, str]] = [
        {
            "metric": "Non-trivial output",
            "pipeline": f"{len(pipe_f1_nt)} / {total}",
            "baseline": f"{len(base_f1_nt)} / {len(base)}",
        },
        _summary_row(
            "Macro-F1 (all runs)",
            statistics.fmean(pipe_f1_all),
            statistics.pstdev(pipe_f1_all),
            statistics.fmean(base_f1_all),
            statistics.pstdev(base_f1_all),
            3,
            "max",
        ),
        _summary_row(
            "Macro-F1 (non-trivial runs)",
            statistics.fmean(pipe_f1_nt) if pipe_f1_nt else 0.0,
            statistics.pstdev(pipe_f1_nt) if pipe_f1_nt else 0.0,
            statistics.fmean(base_f1_nt) if base_f1_nt else 0.0,
            statistics.pstdev(base_f1_nt) if base_f1_nt else 0.0,
            3,
            "max",
        ),
        _summary_row(
            "Input tokens / run (M)",
            statistics.fmean(pipe_it) / 1e6,
            statistics.pstdev(pipe_it) / 1e6,
            statistics.fmean(base_it) / 1e6,
            statistics.pstdev(base_it) / 1e6,
            2,
            "min",
        ),
        _summary_row(
            "Tool calls / run",
            statistics.fmean(pipe_tc),
            statistics.pstdev(pipe_tc),
            statistics.fmean(base_tc),
            statistics.pstdev(base_tc),
            1,
            "min",
        ),
    ]

    with SUMMARY_OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["metric", "pipeline", "baseline"])
        writer.writeheader()
        writer.writerows(rows_out)
    return len(pipe_f1_nt), len(base_f1_nt)


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
    for case, case_label in CASE_DISPLAY.items():
        for arm in ARMS:
            row: dict[str, str] = {"case": case_label, "arm": arm}
            for prompt in PROMPT_KEYS:
                mean, sd = _cell_stats(arms[arm], case, prompt)
                row[f"{prompt}_mean"] = mean
                row[f"{prompt}_sd"] = sd
            rows_out.append(row)

    with CELLS_OUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)


def main() -> int:
    arms = _load_arms()
    pipe_nt, base_nt = _write_summary(arms)
    _write_cells(arms)

    print(
        f"wrote {SUMMARY_OUT.resolve().relative_to(ROOT)} "
        f"(5 metrics, pipeline nontrivial={pipe_nt}/{len(arms['pipeline'])}, "
        f"baseline nontrivial={base_nt}/{len(arms['baseline'])})"
    )
    print(
        f"wrote {CELLS_OUT.resolve().relative_to(ROOT)} "
        f"({len(CASE_DISPLAY)} cases × {len(ARMS)} arms)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
