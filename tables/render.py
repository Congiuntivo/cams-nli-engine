"""Render a TableSpec + its data into a tblr LaTeX fragment."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .latex import escape
from .spec import ColumnSpec, SpanSpec, TableSpec


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
            if col.sd_column is not None:
                raise ValueError(
                    f"{spec.name}: column {col.name!r} has sd_column set "
                    f"but type is {col.type!r}, not 'numeric'"
                )
            continue
        source_cols = [col.name]
        if col.sd_column is not None:
            if col.sd_column not in rows[0]:
                raise ValueError(
                    f"{spec.name}: sd_column {col.sd_column!r} "
                    f"missing from source (paired with {col.name!r})"
                )
            source_cols.append(col.sd_column)
        for r in rows:
            for src in source_cols:
                v = r[src]
                if v in ("", None):
                    continue
                try:
                    float(v)
                except (TypeError, ValueError) as e:
                    raise ValueError(
                        f"{spec.name}: column {src!r} value {v!r} is not numeric"
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
    """Derive an siunitx table-format from data extent + column decimals.

    For ``sd_column`` pairs, append ``(N)`` where ``N == col.decimals`` so
    siunitx accepts the compact-uncertainty payload emitted by ``fmt_cell``.
    """
    if col.table_format:
        return col.table_format
    max_int = 1
    for r in rows:
        v = r[col.name]
        if v in ("", None):
            continue
        max_int = max(max_int, len(f"{abs(float(v)):.0f}"))
    base = str(max_int) if col.decimals == 0 else f"{max_int}.{col.decimals}"
    if col.sd_column is not None:
        base = f"{base}({col.decimals})"
    return base


def fmt_cell(row: dict, col: ColumnSpec) -> str:
    """Format one cell body (no highlight).

    For ``sd_column``-paired numeric columns the output is siunitx
    compact-uncertainty notation ``mean(unc)``, where ``unc`` is the
    standard deviation expressed as trailing digits of the mean's last
    decimal place, zero-padded to ``col.decimals`` width so
    ``separate-uncertainty`` in the preamble renders ``mean \\pm sd``.
    Emitted bare (no ``$...$`` wrapper) so an ``S`` column parses the
    number and ``detect-weight`` propagates ``\\bfseries`` to the digits.
    Either half missing renders as ``{--}``.
    """
    v = row[col.name]
    if v in ("", None):
        return "{--}"
    if col.type == "text":
        return escape(v)
    if col.type == "raw":
        return v
    if col.sd_column is not None:
        sd_raw = row.get(col.sd_column)
        if sd_raw in ("", None):
            return "{--}"
        mean_str = f"{float(v):.{col.decimals}f}"
        unc_digits = round(float(sd_raw) * (10**col.decimals))
        unc_str = f"{unc_digits:0{col.decimals}d}"
        return f"{mean_str}({unc_str})"
    return f"{float(v):.{col.decimals}f}"


def highlighted_indices(col: ColumnSpec, rows: list[dict]) -> set[int]:
    """Row indices whose value is the highlight-best for this column.

    For ``sd_column`` pairs the comparison uses the mean only. When
    ``highlight == "max"`` a cell whose value is exactly ``0.0`` is never
    bolded — this avoids highlighting ``0.000 ± 0.000`` cells as winners.
    """
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
    if col.highlight == "max" and best == 0.0:
        return set()
    return {i for i, v in values if v == best}


def _spans_layout(
    spec: TableSpec, extra: list[SpanSpec] | None = None
) -> list[tuple[str, int, int]]:
    """Return spans as (label, first_col_index_1based, last_col_index_1based).

    ``extra`` supplies per-block spans injected by the ``sections`` feature.
    """
    name_to_index = {c.name: i for i, c in enumerate(spec.columns)}
    all_spans = list(spec.spans) + list(extra or [])
    layout = []
    for span in all_spans:
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


def _colspec_token(col: ColumnSpec, table_format: str | None) -> str:
    """Return the colspec token for one column."""
    if col.type == "text":
        return "X" if col.wrap else "l"
    if col.type == "raw":
        return "c"
    return f"S[table-format={table_format}]"


def _render_block(
    spec: TableSpec,
    rows: list[dict],
    extra_spans: list[SpanSpec] | None = None,
) -> str:
    """Render a single tblr block over ``rows`` (subset of the spec's data)."""
    formats = {
        c.name: infer_table_format(c, rows) for c in spec.columns if c.type == "numeric"
    }
    highlights = {c.name: highlighted_indices(c, rows) for c in spec.columns}

    colspec = " ".join(_colspec_token(c, formats.get(c.name)) for c in spec.columns)

    header_cells = [
        ("{" + escape(c.header) + "}") if c.type == "numeric" else escape(c.header)
        for c in spec.columns
    ]
    header_row = " & ".join(header_cells) + r" \\"

    layout = _spans_layout(spec, extra=extra_spans)
    span_row = span_rules = None
    if layout:
        span_row, span_rules = _span_header_row(spec, layout)
    header_row_count = 2 if span_row else 1

    group_sizes: dict[str, int] = {}
    if spec.row_group and spec.row_group.style == "merge":
        for r in rows:
            key = r[spec.row_group.column]
            group_sizes[key] = group_sizes.get(key, 0) + 1

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
                elif spec.row_group.style == "merge":
                    group_col_idx = next(
                        j
                        for j, c in enumerate(spec.columns)
                        if c.name == spec.row_group.column
                    )
                    lo = group_col_idx + 2 if group_col_idx == 0 else 1
                    body_lines.append(rf"\cmidrule[lr]{{{lo}-{len(spec.columns)}}}")
        cells = []
        for c in spec.columns:
            if (
                spec.row_group
                and spec.row_group.style == "merge"
                and c.name == spec.row_group.column
            ):
                cur = r[c.name]
                if cur != prev_group:
                    size = group_sizes[cur]
                    cells.append(rf"\SetCell[r={size}]{{c}} {fmt_cell(r, c)}")
                else:
                    cells.append("")
                continue
            cell = fmt_cell(r, c)
            if i in highlights[c.name] and cell != "{--}":
                cell = r"\bfseries " + cell
            cells.append(cell)
        if spec.row_group:
            prev_group = r[spec.row_group.column]
        body_lines.append(" & ".join(cells) + r" \\")

    lines = [
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
    return "\n".join(lines)


def _partition_sections(rows: list[dict], column: str) -> list[tuple[str, list[dict]]]:
    """Group rows by ``column`` in first-appearance order."""
    order: list[str] = []
    groups: dict[str, list[dict]] = {}
    for r in rows:
        key = r[column]
        if key not in groups:
            order.append(key)
            groups[key] = []
        groups[key].append(r)
    return [(k, groups[k]) for k in order]


def render(spec: TableSpec, root: Path) -> str:
    """Render the spec + its data into a tblr fragment string.

    When ``spec.sections`` is set the output is one ``tblr`` block per unique
    value of that column (in first-appearance order after sorting), separated
    by ``\\vspace{0.5em}``.
    """
    rows = load_data(spec.source, spec.csv_options)
    validate(spec, rows)
    rows = sort_rows(rows, spec.sort_by)

    try:
        source_display = str(spec.source.relative_to(root))
    except ValueError:
        source_display = str(spec.source)
    header_comment = (
        f"% AUTO-GENERATED from {source_display} by tables/build.py — "
        "do not edit by hand."
    )

    if spec.sections is None:
        return header_comment + "\n" + _render_block(spec, rows) + "\n"

    if spec.sections not in rows[0]:
        raise ValueError(
            f"{spec.name}: sections column {spec.sections!r} not in source"
        )
    span_columns = [c.name for c in spec.columns[1:]]
    if not span_columns:
        raise ValueError(
            f"{spec.name}: sections requires at least two rendered columns "
            f"(got {len(spec.columns)})"
        )
    parts = [header_comment]
    for label, section_rows in _partition_sections(rows, spec.sections):
        extra = [SpanSpec(label=label, columns=list(span_columns))]
        parts.append(_render_block(spec, section_rows, extra_spans=extra))
    return "\n\n\\vspace{0.5em}\n\n".join(parts) + "\n"
