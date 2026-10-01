"""Build the wide CSV consumed by the scratch expert-baseline table.

Scores each expert-authored CARP protocol under ``study/experts/<subject>/{poor,medium,rich}.json``
against the case-003 gold standard via :class:`nli_engine.eval.scoring.hashmatch.HashMatchScore`,
and augments with a reference row per richness for the ``gpt-5.4`` pipeline (mean of the three
runs from ``study/preprocessed/sessions.csv`` / ``hashmatch_fields.csv``). Emits one wide row per
(participant, richness), plus one per (pipeline, richness) — nine rows total.
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from nli_engine.eval.scoring.hashmatch import HashMatchScore  # noqa: E402

EXPERTS_DIR = ROOT / "study" / "experts"
GOLD_PATH = ROOT / "dataset" / "cases" / "003_expected.json"
SESSIONS = Path(__file__).parent / "sessions.csv"
HM_FIELDS = Path(__file__).parent / "hashmatch_fields.csv"
OUTPUT = Path(__file__).parent / "experts_scratch_wide.csv"
HEADLINE_OUTPUT = Path(__file__).parent / "experts_headline_wide.csv"
PERFIELD_OUTPUT = Path(__file__).parent / "experts_perfield_transposed.csv"

RICHNESS_KEYS = ["poor", "medium", "rich"]
RICHNESS_LABELS = {"poor": "Poor", "medium": "Medium", "rich": "Rich"}

FIELDS = [
    "primaryDevices",
    "connectedDevices",
    "tasks",
    "triggers",
    "taskControls",
    "connections",
    "applicationData",
    "other",
]

SUBJECT_META = {
    "subject01": "Main architect (10y)",
    "subject02": "Software Developer (1y)",
}

PIPELINE_LABEL = "pipeline (gpt-5.4)"


def _score_expert(path: Path, gold: dict) -> dict[str, float]:
    """Score one expert JSON, returning ``{'macro_f1': ..., <field>: ...}``."""
    actual = json.loads(path.read_text())
    score = HashMatchScore.compute(actual, gold)
    out: dict[str, float] = {"macro_f1": score.f1}
    for field in FIELDS:
        fs = score.per_field.get(field)
        out[field] = fs.f1 if fs is not None else 0.0
    return out


def _load_participant_meta() -> dict[str, tuple[str, int]]:
    """Load role and confidence per (subject, richness) from ``study/experts/data.csv``.

    Returns a dict mapping subject_id ``"subject0N"`` to ``(role_or_years, {richness: confidence})``,
    but flattened as ``{subject_id: {"role": str, "conf": {richness: int}}}``.
    """
    meta: dict[str, dict] = {}
    with (EXPERTS_DIR / "data.csv").open() as fh:
        rows = list(csv.DictReader(fh))
    # data.csv has one row per subject in filesystem order (subject01, subject02).
    for i, r in enumerate(rows, start=1):
        sid = f"subject{i:02d}"
        meta[sid] = {
            "conf": {
                "poor": r["confidence_poor"],
                "medium": r["confidence_medium"],
                "rich": r["confidence_rich"],
            }
        }
    return meta


def _pipeline_stats() -> dict[str, dict[str, float]]:
    """Aggregate gpt-5.4 case-003 per-richness macro-F1 and per-field F1 over the three runs."""
    with SESSIONS.open() as fh:
        sessions = [
            r
            for r in csv.DictReader(fh)
            if r["source"] == "models"
            and r["model"] == "gpt-5.4"
            and r["case_id"] == "003_cardio_wellness"
        ]
    with HM_FIELDS.open() as fh:
        fields_rows = list(csv.DictReader(fh))

    sessions_by_richness: dict[str, list[dict]] = {k: [] for k in RICHNESS_KEYS}
    for r in sessions:
        pk = r["prompt_key"]
        if pk in sessions_by_richness:
            sessions_by_richness[pk].append(r)

    result: dict[str, dict[str, float]] = {}
    for richness, rows in sessions_by_richness.items():
        session_ids = {r["session_id"] for r in rows}
        macro = statistics.fmean(float(r["hm_f1"]) for r in rows)
        stats: dict[str, float] = {"macro_f1": macro}
        for field in FIELDS:
            vals = [
                float(fr["f1"])
                for fr in fields_rows
                if fr["session_id"] in session_ids and fr["field_name"] == field
            ]
            stats[field] = statistics.fmean(vals) if vals else 0.0
        result[richness] = stats
    return result


def _fmt(v: float) -> str:
    return repr(v)


def main() -> int:
    gold = json.loads(GOLD_PATH.read_text())
    meta = _load_participant_meta()
    pipeline = _pipeline_stats()

    fieldnames = ["who", "richness", "role_or_years", "confidence", "macro_f1", *FIELDS]
    rows_out: list[dict[str, str]] = []

    for sid in ("subject01", "subject02"):
        role = SUBJECT_META[sid]
        for richness in RICHNESS_KEYS:
            stats = _score_expert(EXPERTS_DIR / sid / f"{richness}.json", gold)
            row: dict[str, str] = {
                "who": sid,
                "richness": RICHNESS_LABELS[richness],
                "role_or_years": role,
                "confidence": meta[sid]["conf"][richness],
                "macro_f1": _fmt(stats["macro_f1"]),
            }
            for field in FIELDS:
                row[field] = _fmt(stats[field])
            rows_out.append(row)

    for richness in RICHNESS_KEYS:
        stats = pipeline[richness]
        row = {
            "who": PIPELINE_LABEL,
            "richness": RICHNESS_LABELS[richness],
            "role_or_years": "—",
            "confidence": "—",
            "macro_f1": _fmt(stats["macro_f1"]),
        }
        for field in FIELDS:
            row[field] = _fmt(stats[field])
        rows_out.append(row)

    with OUTPUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    print(
        f"wrote {OUTPUT.resolve().relative_to(ROOT)} "
        f"(9 rows: 2 subjects × 3 richness + pipeline × 3 richness)"
    )

    _write_headline(rows_out)
    print(
        f"wrote {HEADLINE_OUTPUT.resolve().relative_to(ROOT)} "
        f"(3 rows: 2 subjects + pipeline, pivoted across richness)"
    )

    _write_perfield_transposed(rows_out)
    print(
        f"wrote {PERFIELD_OUTPUT.resolve().relative_to(ROOT)} "
        f"(8 rows: one per field, columns pivoted across agent × richness)"
    )
    return 0


def _write_headline(long_rows: list[dict[str, str]]) -> None:
    """Pivot the long per-(agent, richness) rows into one wide row per agent.

    Emits ``experts_headline_wide.csv`` for the §4.6 headline table: one row per
    agent with ``f1_<richness>`` and ``conf_<richness>`` columns alongside ``who``
    and ``role``. The pipeline's conf cells remain em-dashes.
    """
    agents = ["subject01", "subject02", PIPELINE_LABEL]
    by_agent: dict[str, dict[str, dict[str, str]]] = {a: {} for a in agents}
    for r in long_rows:
        by_agent[r["who"]][r["richness"]] = r

    fieldnames = [
        "who",
        "role",
        "f1_poor",
        "conf_poor",
        "f1_medium",
        "conf_medium",
        "f1_rich",
        "conf_rich",
    ]
    with HEADLINE_OUTPUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for who in agents:
            poor = by_agent[who]["Poor"]
            medium = by_agent[who]["Medium"]
            rich = by_agent[who]["Rich"]
            writer.writerow(
                {
                    "who": who,
                    "role": poor["role_or_years"],
                    "f1_poor": poor["macro_f1"],
                    "conf_poor": poor["confidence"],
                    "f1_medium": medium["macro_f1"],
                    "conf_medium": medium["confidence"],
                    "f1_rich": rich["macro_f1"],
                    "conf_rich": rich["confidence"],
                }
            )


def _write_perfield_transposed(long_rows: list[dict[str, str]]) -> None:
    """Transpose the per-field table so fields are rows and (agent × richness) are columns.

    Emits ``experts_perfield_transposed.csv`` for the §4.6 per-field breakdown
    rendered with 8 rows (one per CARP field) and 9 numeric columns grouped
    into three per-agent spans (Poor/Medium/Rich).
    """
    agents = [
        ("subject01", "subject01"),
        ("subject02", "subject02"),
        (PIPELINE_LABEL, "pipeline"),
    ]
    by_key: dict[tuple[str, str], dict[str, str]] = {
        (r["who"], r["richness"]): r for r in long_rows
    }

    fieldnames = ["field"]
    for _, slug in agents:
        for richness in ("poor", "medium", "rich"):
            fieldnames.append(f"{slug}_{richness}")

    with PERFIELD_OUTPUT.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for field in FIELDS:
            row = {"field": field}
            for who, slug in agents:
                for richness in ("Poor", "Medium", "Rich"):
                    row[f"{slug}_{richness.lower()}"] = by_key[(who, richness)][field]
            writer.writerow(row)


if __name__ == "__main__":
    sys.exit(main())
