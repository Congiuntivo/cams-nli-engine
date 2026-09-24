"""Render a TableSpec + its data into a tblr LaTeX fragment."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .latex import escape
from .spec import ColumnSpec, TableSpec


def load_data(source: Path, csv_options: dict) -> list[dict]:
    """Load a CSV or JSON file into a list of row dicts.

    JSON sources must be a list of flat objects; nested normalization is out of scope
    until a spec that needs it appears.
    """
    if source.suffix == ".json":
        data = json.loads(source.read_text())
        if not isinstance(data, list):
            raise ValueError(f"{source}: JSON must be a list of objects")
        return [
            {k: str(v) if v is not None else "" for k, v in row.items()} for row in data
        ]
    comment = csv_options.get("comment")
    with source.open() as fh:
        lines = [ln for ln in fh if not (comment and ln.startswith(comment))]
    return list(csv.DictReader(lines))


def validate(spec: TableSpec, rows: list[dict]) -> None:
    """Check columns exist and numeric values parse; fail loudly otherwise."""
    if not rows:
        raise ValueError(f"{spec.name}: source has no data rows")
    for col in spec.columns:
        if col.name not in rows[0]:
            raise ValueError(f"{spec.name}: column {col.name!r} missing from source")
        if col.type != "numeric":
            continue
        for r in rows:
            v = r[col.name]
            if v in ("", None):
                continue
            try:
                float(v)
            except (TypeError, ValueError) as e:
                raise ValueError(
                    f"{spec.name}: column {col.name!r} value {v!r} is not numeric"
                ) from e
    # Validate explicit table_format widths (inferred formats are wide by construction).
    for col in spec.columns:
        if col.type != "numeric" or not col.table_format:
            continue
        int_width, _, dec_width = col.table_format.partition(".")
        int_width = int(int_width)
        for r in rows:
            v = r[col.name]
            if v in ("", None):
                continue
            got = len(f"{abs(float(v)):.0f}")
            if got > int_width:
                raise ValueError(
                    f"{spec.name}: column {col.name!r} table-format integer width "
                    f"{int_width} too narrow for value {v!r} (needs {got})"
                )


def sort_rows(rows: list[dict], sort_by) -> list[dict]:
    """Sort rows by the given SortSpecs (stable, applied last-key-first)."""
    for s in reversed(sort_by):
        if s.order:
            index = {v: i for i, v in enumerate(s.order)}
            rows = sorted(rows, key=lambda r: index.get(r[s.column], len(index)))
        else:
            rows = sorted(rows, key=lambda r: r[s.column])
    return rows


def infer_table_format(col: ColumnSpec, rows: list[dict]) -> str:
    """Derive an siunitx table-format from data extent + column decimals."""
    if col.table_format:
        return col.table_format
    max_int = 1
    for r in rows:
        v = r[col.name]
        if v in ("", None):
            continue
        max_int = max(max_int, len(f"{abs(float(v)):.0f}"))
    return str(max_int) if col.decimals == 0 else f"{max_int}.{col.decimals}"


def fmt_cell(v: str, col: ColumnSpec) -> str:
    """Format one cell body (no highlight)."""
    if v in ("", None):
        return "{--}"
    if col.type == "text":
        return escape(v)
    return f"{float(v):.{col.decimals}f}"


def highlighted_indices(col: ColumnSpec, rows: list[dict]) -> set[int]:
    """Row indices whose value is the highlight-best for this column."""
    if not col.highlight:
        return set()
    values = [
        (i, float(r[col.name]))
        for i, r in enumerate(rows)
        if r[col.name] not in ("", None)
    ]
    if not values:
        return set()
    best = (
        max(v for _, v in values)
        if col.highlight == "max"
        else min(v for _, v in values)
    )
    return {i for i, v in values if v == best}


def _spans_layout(spec: TableSpec) -> list[tuple[str, int, int]]:
    """Return spans as (label, first_col_index_1based, last_col_index_1based)."""
    name_to_index = {c.name: i for i, c in enumerate(spec.columns)}
    layout = []
    for span in spec.spans:
        indices = [name_to_index[c] for c in span.columns]
        if indices != list(range(min(indices), max(indices) + 1)):
            raise ValueError(
                f"{spec.name}: span {span.label!r} columns are not contiguous"
            )
        layout.append((span.label, min(indices) + 1, max(indices) + 1))
    return layout


def _span_header_row(
    spec: TableSpec, layout: list[tuple[str, int, int]]
) -> tuple[str, list[str]]:
    """Build the spanning-header row and the \\cmidrule lines beneath it."""
    ncols = len(spec.columns)
    covered = {}
    for label, lo, hi in layout:
        covered[lo] = (label, hi)
    cells = []
    i = 1
    while i <= ncols:
        if i in covered:
            label, hi = covered[i]
            span_n = hi - i + 1
            cells.append(rf"\SetCell[c={span_n}]{{c}} {escape(label)}")
            cells.extend([""] * (span_n - 1))
            i = hi + 1
        else:
            cells.append("")
            i += 1
    row = " & ".join(cells) + r" \\"
    rules = [rf"\cmidrule[lr]{{{lo}-{hi}}}" for _, lo, hi in layout]
    return row, rules


def render(spec: TableSpec, root: Path) -> str:
    """Render the spec + its data into a tblr fragment string."""
    rows = load_data(spec.source, spec.csv_options)
    validate(spec, rows)
    rows = sort_rows(rows, spec.sort_by)

    formats = {
        c.name: infer_table_format(c, rows) for c in spec.columns if c.type == "numeric"
    }
    highlights = {c.name: highlighted_indices(c, rows) for c in spec.columns}

    colspec = " ".join(
        ("X" if c.wrap else "l")
        if c.type == "text"
        else f"S[table-format={formats[c.name]}]"
        for c in spec.columns
    )

    header_cells = [
        ("{" + escape(c.header) + "}") if c.type == "numeric" else escape(c.header)
        for c in spec.columns
    ]
    header_row = " & ".join(header_cells) + r" \\"

    layout = _spans_layout(spec)
    span_row = span_rules = None
    if layout:
        span_row, span_rules = _span_header_row(spec, layout)
    header_row_count = 2 if span_row else 1

    body_lines = []
    prev_group = object()
    for i, r in enumerate(rows):
        if spec.row_group and i > 0:
            cur = r[spec.row_group.column]
            if cur != prev_group:
                if spec.row_group.style == "cmidrule":
                    body_lines.append(rf"\cmidrule[lr]{{1-{len(spec.columns)}}}")
                elif spec.row_group.style == "label":
                    body_lines.append(
                        rf"\SetCell[c={len(spec.columns)}]{{l}} {escape(cur)}"
                        + " & " * (len(spec.columns) - 1)
                        + r"\\"
                    )
        if spec.row_group:
            prev_group = r[spec.row_group.column]
        cells = []
        for c in spec.columns:
            cell = fmt_cell(r[c.name], c)
            if i in highlights[c.name] and cell != "{--}":
                cell = r"\bfseries " + cell
            cells.append(cell)
        body_lines.append(" & ".join(cells) + r" \\")

    try:
        source_display = str(spec.source.relative_to(root))
    except ValueError:
        source_display = str(spec.source)

    lines = [
        f"% AUTO-GENERATED from {source_display} by tables/build.py — do not edit by hand.",
        r"\begin{tblr}{",
        f"  colspec = {{{colspec}}},",
        f"  row{{1-{header_row_count}}} = {{guard, font=\\bfseries}},"
        if header_row_count > 1
        else r"  row{1} = {guard, font=\bfseries},",
        r"}",
        r"\toprule",
    ]
    if span_row:
        lines.append(span_row)
        lines.extend(span_rules)
    lines.append(header_row)
    lines.append(r"\midrule")
    lines.extend(body_lines)
    lines.append(r"\bottomrule")
    lines.append(r"\end{tblr}")
    return "\n".join(lines) + "\n"
