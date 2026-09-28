"""Render a PlotSpec + its data into a matplotlib Figure."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.path import Path as MplPath

from .spec import PlotSpec
from .style import INK, MUTED, STROKE_MEDIUM, STROKE_THIN, apply_style, series_palette

_IBEAM_MARKER = MplPath(
    vertices=[
        (-0.5, 0.5),
        (0.5, 0.5),
        (0.0, 0.5),
        (0.0, -0.5),
        (-0.5, -0.5),
        (0.5, -0.5),
    ],
    codes=[
        MplPath.MOVETO,
        MplPath.LINETO,
        MplPath.MOVETO,
        MplPath.LINETO,
        MplPath.MOVETO,
        MplPath.LINETO,
    ],
)


def _apply_filter(df: pd.DataFrame, allow: dict[str, list[str]]) -> pd.DataFrame:
    for col, allowed in allow.items():
        if col not in df.columns:
            raise ValueError(f"filter column {col!r} missing from source")
        df = df[df[col].isin(allowed)]
    return df.reset_index(drop=True)


def _as_ordered_categorical(series: pd.Series, order: list[str] | None) -> pd.Series:
    if order is None:
        return series
    return pd.Categorical(series, categories=order, ordered=True)


def render_small_multiples_line(spec: PlotSpec, root: Path) -> Figure:
    """Render a small-multiples line chart (one panel per facet value).

    Draws one line per hue value at the mean of ``y`` across runs. When
    ``spec.aggregate.errorbar == "sd"`` an error bar of +/-1 standard
    deviation is drawn at each point (seaborn ``lineplot`` estimator).
    """
    apply_style()

    df = pd.read_csv(spec.source)
    df = _apply_filter(df, spec.filter.allow)
    df = df.dropna(subset=[spec.y.column]).reset_index(drop=True)
    if df.empty:
        raise ValueError(f"{spec.name}: no rows after filter + NaN drop")

    df[spec.x.column] = _as_ordered_categorical(df[spec.x.column], spec.x.order)
    df[spec.hue.column] = _as_ordered_categorical(df[spec.hue.column], spec.hue.order)
    df[spec.facet.column] = _as_ordered_categorical(
        df[spec.facet.column], spec.facet.order
    )

    facet_order = spec.facet.order or sorted(df[spec.facet.column].dropna().unique())
    hue_order = spec.hue.order or sorted(df[spec.hue.column].dropna().unique())
    palette = list(series_palette()[: len(hue_order)])
    color_by_hue = dict(zip(hue_order, palette))

    errorbar_arg = (
        spec.aggregate.errorbar if spec.aggregate.errorbar != "none" else None
    )

    fig, axes = plt.subplots(
        1,
        len(facet_order),
        sharey=True,
        figsize=spec.figure.figsize,
        constrained_layout=True,
    )
    if len(facet_order) == 1:
        axes = [axes]

    for ax, facet_value in zip(axes, facet_order):
        raw_f = df[df[spec.facet.column] == facet_value]
        sns.pointplot(
            data=raw_f,
            x=spec.x.column,
            y=spec.y.column,
            hue=spec.hue.column,
            hue_order=hue_order,
            palette=palette,
            estimator="mean",
            errorbar=errorbar_arg,
            dodge=spec.aggregate.dodge if spec.aggregate.dodge > 0 else False,
            capsize=0.08,
            err_kws={"linewidth": STROKE_THIN},
            marker="o",
            markersize=3.5,
            linestyle="none",
            ax=ax,
            legend=False,
        )
        if spec.facet.labels:
            title = spec.facet.labels.get(facet_value, str(facet_value))
        else:
            title = spec.facet.title_template.format(value=facet_value)
        ax.set_title(title)
        ax.set_xlabel(spec.x.label or "")
        ax.set_ylabel("")
        if spec.y.limit is not None:
            ax.set_ylim(*spec.y.limit)

    axes[0].set_ylabel(spec.y.label or "")

    handles = [
        Line2D(
            [0],
            [0],
            color=color_by_hue[h],
            marker="o",
            linewidth=STROKE_MEDIUM,
            label=str(h),
        )
        for h in hue_order
    ]
    if spec.aggregate.errorbar == "sd":
        handles.append(
            Line2D(
                [0],
                [0],
                color=MUTED,
                linestyle="none",
                marker=_IBEAM_MARKER,
                markersize=5,
                markeredgewidth=STROKE_THIN,
                label="±1 SD",
            )
        )
    fig.legend(
        handles=handles,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        frameon=False,
        title=spec.hue.title,
    )
    return fig


def render_grouped_bar(spec: PlotSpec, root: Path) -> Figure:
    """Render a single-panel grouped bar chart (bars grouped by hue at each x).

    Bars show the mean of ``y`` across the sessions matching each
    (x, hue) cell; when ``spec.aggregate.errorbar == "sd"`` an error bar of
    +/-1 standard deviation is drawn at each bar top.

    Args:
        spec: Loaded plot spec. Must not carry a ``facet``; ``aggregate.method``
            must be ``"mean"`` and ``aggregate.dodge`` must be ``0`` (bar
            grouping handles the horizontal offset natively).
        root: Repository root (used for resolving relative paths; the source
            is already absolute by the time it reaches this function).

    Raises:
        ValueError: If the spec carries a facet, a non-mean method, or a
            non-zero dodge; or if the filtered data is empty.
    """
    if spec.facet is not None:
        raise ValueError(
            f"{spec.name}: grouped_bar does not support facets (spec.facet must be None)"
        )
    if spec.aggregate.method != "mean":
        raise ValueError(
            f"{spec.name}: grouped_bar only supports aggregate.method='mean', "
            f"got {spec.aggregate.method!r}"
        )
    if spec.aggregate.dodge != 0:
        raise ValueError(
            f"{spec.name}: grouped_bar does not support aggregate.dodge != 0 "
            "(bar grouping handles the offset natively)"
        )

    apply_style()

    df = pd.read_csv(spec.source)
    df = _apply_filter(df, spec.filter.allow)
    df = df.dropna(subset=[spec.y.column]).reset_index(drop=True)
    if df.empty:
        raise ValueError(f"{spec.name}: no rows after filter + NaN drop")

    df[spec.x.column] = _as_ordered_categorical(df[spec.x.column], spec.x.order)
    df[spec.hue.column] = _as_ordered_categorical(df[spec.hue.column], spec.hue.order)

    x_order = spec.x.order or sorted(df[spec.x.column].dropna().unique())
    hue_order = spec.hue.order or sorted(df[spec.hue.column].dropna().unique())
    palette = list(series_palette()[: len(hue_order)])

    errorbar_arg = (
        spec.aggregate.errorbar if spec.aggregate.errorbar != "none" else None
    )

    fig, ax = plt.subplots(1, 1, figsize=spec.figure.figsize, constrained_layout=True)
    sns.barplot(
        data=df,
        x=spec.x.column,
        y=spec.y.column,
        hue=spec.hue.column,
        order=x_order,
        hue_order=hue_order,
        palette=palette,
        estimator="mean",
        errorbar=errorbar_arg,
        capsize=0.15,
        err_kws={"linewidth": STROKE_THIN, "color": MUTED},
        edgecolor=INK,
        linewidth=STROKE_THIN * 0.5,
        ax=ax,
        legend=False,
    )
    ax.set_xlabel(spec.x.label or "")
    ax.set_ylabel(spec.y.label or "")
    if spec.y.limit is not None:
        ax.set_ylim(*spec.y.limit)

    hue_label_map = spec.hue.labels or {}
    handles = [
        Patch(
            facecolor=palette[i],
            edgecolor=INK,
            linewidth=STROKE_THIN * 0.5,
            label=hue_label_map.get(str(h), str(h)),
        )
        for i, h in enumerate(hue_order)
    ]
    if spec.aggregate.errorbar == "sd":
        handles.append(
            Line2D(
                [0],
                [0],
                color=MUTED,
                linestyle="none",
                marker=_IBEAM_MARKER,
                markersize=5,
                markeredgewidth=STROKE_THIN,
                label="±1 SD",
            )
        )
    fig.legend(
        handles=handles,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        frameon=False,
        title=spec.hue.title,
    )
    return fig


RENDERERS: dict[str, Callable[[PlotSpec, Path], Figure]] = {
    "small_multiples_line": render_small_multiples_line,
    "grouped_bar": render_grouped_bar,
}


def render(spec: PlotSpec, root: Path) -> Figure:
    """Dispatch to the renderer registered under ``spec.kind``."""
    try:
        fn = RENDERERS[spec.kind]
    except KeyError as e:
        raise ValueError(f"{spec.name}: unknown plot kind {spec.kind!r}") from e
    return fn(spec, root)
