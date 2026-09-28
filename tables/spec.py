"""Table spec dataclasses and YAML loader."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ColumnSpec:
    """One CSV/output column.

    Attributes:
        name: Column name in the source data.
        header: Display header (sentence case, units included).
        type: ``"text"``, ``"numeric"``, or ``"raw"``. Raw cells are emitted
            verbatim (no escaping, no formatting, no highlight) and get a
            centred ``c`` colspec — use for pre-formatted LaTeX content that
            does not fit the ``S`` column contract.
        decimals: Fixed decimal places for numeric columns.
        table_format: siunitx ``table-format`` string; inferred from data if omitted.
        wrap: For text columns, use ``X`` colspec instead of ``l``.
        highlight: ``"max"`` or ``"min"`` — bolds the extremum (ties all bolded).
            When ``"max"``, a value of exactly ``0.0`` is never bolded (avoids
            highlighting ``0.000 ± 0.000`` cells as the "winner").
        sd_column: Numeric only. When set, the cell renders as ``mean \\pm sd``
            using ``name`` as the mean and ``sd_column`` as the sd source.
            Highlight comparison uses the mean alone; ``table-format`` is
            inferred from the mean only.
    """

    name: str
    header: str
    type: str
    decimals: int = 0
    table_format: str | None = None
    wrap: bool = False
    highlight: str | None = None
    sd_column: str | None = None


@dataclass
class SortSpec:
    """Sort by a column, optionally with an explicit categorical order.

    Attributes:
        column: Column to sort by.
        order: If given, sort using this categorical order; else lexicographic.
    """

    column: str
    order: list[str] | None = None


@dataclass
class SpanSpec:
    """Spanning header label above a contiguous run of columns.

    Attributes:
        label: Group label displayed in the spanning row.
        columns: Ordered list of column names covered (must be contiguous).
    """

    label: str
    columns: list[str]


@dataclass
class RowGroupSpec:
    """Insert a rule or label row when the given column's value changes.

    Attributes:
        column: Column whose value transitions trigger the group break.
        style: ``"cmidrule"`` for a full-width rule, ``"label"`` for a label row,
            ``"merge"`` for a vertically-merged cell in the group column that spans
            the group's rows (via ``\\SetCell[r=n]{c}``).
    """

    column: str
    style: str = "cmidrule"


@dataclass
class TableSpec:
    """Full spec for one output table.

    Attributes:
        name: Output filename stem (produces ``tables/<name>.tex``).
        source: Absolute path to the CSV or JSON source.
        columns: Ordered ColumnSpec list.
        csv_options: Passed to the CSV loader (e.g. ``{"comment": "#"}``).
        sort_by: Ordered list of SortSpec applied stably.
        spans: Optional spanning header groups.
        row_group: Optional row-grouping rule.
        sections: Optional column name. When set, rows are partitioned by
            that column's value and emitted as one ``tblr`` block per section
            (each block gets a spanning header carrying the section value
            over every column except the first, and highlights are computed
            per-block). The sections column itself is not rendered.
        spec_path: Path to the YAML spec file (for diagnostics).
    """

    name: str
    source: Path
    columns: list[ColumnSpec]
    csv_options: dict = field(default_factory=dict)
    sort_by: list[SortSpec] = field(default_factory=list)
    spans: list[SpanSpec] = field(default_factory=list)
    row_group: RowGroupSpec | None = None
    sections: str | None = None
    spec_path: Path | None = None


def load_spec(path: Path, root: Path) -> TableSpec:
    """Load a table spec from YAML; ``source`` resolves against ``root``."""
    data = yaml.safe_load(path.read_text())
    return TableSpec(
        name=data["name"],
        source=(root / data["source"]).resolve(),
        columns=[ColumnSpec(**c) for c in data["columns"]],
        csv_options=data.get("csv_options", {}),
        sort_by=[SortSpec(**s) for s in data.get("sort_by", [])],
        spans=[SpanSpec(**s) for s in data.get("spans", [])],
        row_group=RowGroupSpec(**data["row_group"]) if data.get("row_group") else None,
        sections=data.get("sections"),
        spec_path=path.resolve(),
    )
