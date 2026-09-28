"""Persist accumulated preprocess rows to the on-disk table layout.

Layout produced under ``out_dir``::

    sessions.csv
    steps.csv
    tools.csv
    hashmatch_fields.csv
    workflow_configs.csv
    protocols/<session_id>.json      # actual protocol per run
    expected/<case_id>.json          # ground-truth protocol per case
    skipped.csv                      # (source, filename, reason)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Sequence


def write_tables(
    combined: dict[str, list[dict[str, Any]]],
    protocols: dict[str, dict[str, Any] | None],
    expected: dict[str, dict[str, Any]],
    skipped: Sequence[tuple[str, str, str]],
    out_dir: Path,
) -> None:
    """Write the five CSVs plus per-session and per-case protocol JSON dumps.

    Args:
        combined: Merged row lists keyed by table name (``sessions``,
            ``steps``, ``tools``, ``hashmatch_fields``, ``workflow_configs``).
        protocols: ``session_id -> actual protocol dict`` (may be None for
            failed runs; those files are skipped).
        expected: ``case_id -> expected protocol dict``.
        skipped: Tuples of ``(source_name, filename, reason)``.
        out_dir: Destination directory. Created if missing.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    for table_name, rows in combined.items():
        _write_csv(out_dir / f"{table_name}.csv", rows)

    proto_dir = out_dir / "protocols"
    proto_dir.mkdir(exist_ok=True)
    for session_id, protocol in protocols.items():
        if protocol is None:
            continue
        with (proto_dir / f"{session_id}.json").open("w") as fh:
            json.dump(protocol, fh, indent=2)

    exp_dir = out_dir / "expected"
    exp_dir.mkdir(exist_ok=True)
    for case_id, protocol in expected.items():
        with (exp_dir / f"{case_id}.json").open("w") as fh:
            json.dump(protocol, fh, indent=2)

    _write_csv(
        out_dir / "skipped.csv",
        [{"source": s, "filename": f, "reason": r} for s, f, r in skipped],
    )


def _write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    if not rows:
        path.write_text("")
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
