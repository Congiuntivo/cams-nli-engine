"""Plot spec dataclasses and YAML loader."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class FilterSpec:
    """Allowlist filter applied row-wise before plotting.

    Attributes:
        allow: Mapping ``column -> permitted values``. Conditions AND-ed
            across columns; a row is kept only if every named column's value
            is in its allowlist.
    """

    allow: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class AxisSpec:
    """Categorical axis (x-axis).

    Attributes:
        column: Source column name.
        order: Explicit categorical order; controls tick order left-to-right.
        label: Axis label. If ``None`` the axis is unlabeled.
    """

    column: str
    order: list[str] | None = None
    label: str | None = None


@dataclass
class YSpec:
    """Continuous y-axis.

    Attributes:
        column: Source column name (numeric).
        label: Axis label; shown only on the leftmost facet.
        limit: ``(y_min, y_max)`` clamp; identical across facets.
    """

    column: str
    label: str | None = None
    limit: tuple[float, float] | None = None


@dataclass
class HueSpec:
    """Series grouping (one line/color per hue value).

    Attributes:
        column: Source column name.
        order: Explicit categorical order; controls legend order and palette
            assignment.
        title: Legend title.
        labels: Optional explicit legend label per hue value. When provided,
            entries in the legend take their text from this map; missing keys
            fall back to the raw value.
    """

    column: str
    order: list[str] | None = None
    title: str | None = None
    labels: dict[str, str] | None = None


@dataclass
class FacetSpec:
    """Small-multiples facet column.

    Attributes:
        column: Source column name.
        order: Explicit categorical order; controls panel order left-to-right.
        title_template: Python format string; receives ``value`` (the facet
            column value) as keyword argument. Ignored when ``labels`` is set.
        labels: Optional explicit display label per facet value. When
            provided, ``title_template`` is ignored and each panel takes its
            title from this map; missing keys fall back to the raw value.
    """

    column: str
    order: list[str] | None = None
    title_template: str = "{value}"
    labels: dict[str, str] | None = None


@dataclass
class AggregateSpec:
    """How raw runs collapse into series points.

    Attributes:
        by: Grouping columns whose combination defines one aggregated point.
        method: Aggregation function name. Currently only ``"mean"`` is used
            by the small-multiples renderer.
        errorbar: Variance indicator at each point. ``"sd"`` for +/-1
            standard deviation, ``"none"`` to draw the line only.
        dodge: Horizontal offset between hue groups at each x tick, as a
            fraction of the categorical spacing. ``0`` disables dodging.
            Useful when many hue series with error bars would otherwise
            stack on top of each other.
    """

    by: list[str]
    method: str = "mean"
    errorbar: str = "sd"
    dodge: float = 0.0


@dataclass
class FigureSpec:
    """Figure-level layout knobs.

    Attributes:
        figsize: ``(width, height)`` in inches; drives the PDF page size.
        legend: One of ``"right"``, ``"top"``, ``"bottom"``. Currently only
            ``"right"`` is implemented.
    """

    figsize: tuple[float, float] = (7.0, 2.6)
    legend: str = "right"


@dataclass
class PlotSpec:
    """Full spec for one output plot.

    Attributes:
        name: Output filename stem (produces ``plots/<name>.pdf``).
        kind: Renderer key; must match a registered renderer in
            :data:`plots.render.RENDERERS`.
        source: Absolute path to the source CSV (resolved from repo root at
            load time).
        filter: Row filter (allowlist per column).
        x: Categorical x-axis spec.
        y: Continuous y-axis spec.
        hue: Series grouping spec.
        facet: Small-multiples facet spec.
        aggregate: How raw runs collapse into series points.
        figure: Figure-level layout.
        spec_path: Path to the YAML spec file (for diagnostics).
    """

    name: str
    kind: str
    source: Path
    filter: FilterSpec
    x: AxisSpec
    y: YSpec
    hue: HueSpec
    aggregate: AggregateSpec
    figure: FigureSpec
    facet: FacetSpec | None = None
    spec_path: Path | None = None


def _limit(raw) -> tuple[float, float] | None:
    if raw is None:
        return None
    lo, hi = raw
    return (float(lo), float(hi))


def _figsize(raw) -> tuple[float, float]:
    if raw is None:
        return (7.0, 2.6)
    w, h = raw
    return (float(w), float(h))


def load_spec(path: Path, root: Path) -> PlotSpec:
    """Load a plot spec from YAML; ``source`` resolves against ``root``."""
    data = yaml.safe_load(path.read_text())
    return PlotSpec(
        name=data["name"],
        kind=data["kind"],
        source=(root / data["source"]).resolve(),
        filter=FilterSpec(allow=data.get("filter", {}).get("allow", {})),
        x=AxisSpec(**data["x"]),
        y=YSpec(
            column=data["y"]["column"],
            label=data["y"].get("label"),
            limit=_limit(data["y"].get("limit")),
        ),
        hue=HueSpec(**data["hue"]),
        facet=FacetSpec(**data["facet"]) if "facet" in data else None,
        aggregate=AggregateSpec(**data["aggregate"]),
        figure=FigureSpec(
            figsize=_figsize(data.get("figure", {}).get("figsize")),
            legend=data.get("figure", {}).get("legend", "right"),
        ),
        spec_path=path.resolve(),
    )
