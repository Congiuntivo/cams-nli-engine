"""Central style tokens for every plot.

Ports the palette, type sizes, and stroke widths from the thesis typst
module ``thesis/diagrams/_lib/style.typ`` so diagrams and plots read as a
family. Every hex value here must appear verbatim in the typst file;
``verify_palette_matches_typst`` enforces the invariant.

Every plot renderer calls :func:`apply_style` before drawing. Renderers
must not set their own colors, font sizes, or stroke widths -- read them
from the constants exposed here.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import matplotlib as mpl
import seaborn as sns

# ---------------------------------------------------------------------------
# COLORS -- keep in sync with thesis/diagrams/_lib/style.typ
# ---------------------------------------------------------------------------

INK = "#1a1a1a"
MUTED = "#5a5a5a"
PRIMARY = "#2c5c8a"
ACCENT = "#c96a1d"
SURFACE = "#ffffff"
ACCENT_FILL = "#fbeedd"
ENVELOPE_FILL = "#fbf7e6b2"
ENVELOPE_STROKE = "#8a7d3d"

# (fill, stroke) pairs; index matches typst layer-accents 1..5.
LAYER_ACCENTS: list[tuple[str, str]] = [
    ("#dbe7dc", "#4a8f5c"),  # 1 -- green
    ("#f6dfbe", "#c98a2b"),  # 2 -- amber
    ("#dcd7ee", "#6d5cae"),  # 3 -- purple
    ("#edd8de", "#e82f82"),  # 4 -- rose
    (SURFACE, MUTED),  # 5 -- neutral
]

# ---------------------------------------------------------------------------
# TYPOGRAPHY
# ---------------------------------------------------------------------------

TEXT_TINY = 7.0
TEXT_SMALL = 8.0
TEXT_BODY = 9.0
TEXT_HEADER = 9.5

FONT_STACK = ["New Computer Modern", "CMU Serif", "Latin Modern Roman", "DejaVu Serif"]

# ---------------------------------------------------------------------------
# STROKES
# ---------------------------------------------------------------------------

STROKE_THIN = 1.0
STROKE_MEDIUM = 1.2
STROKE_THICK = 1.5

GRID_COLOR = "#e5e5e5"


@lru_cache(maxsize=1)
def series_palette() -> tuple[str, ...]:
    """Return the seaborn ``colorblind`` palette as a tuple of hex strings.

    Cached because ``sns.color_palette`` is not free and every renderer needs it.
    """
    return tuple(sns.color_palette("colorblind").as_hex())


def apply_style() -> None:
    """Configure seaborn theme and matplotlib rcParams for consistent plots.

    Sets a whitegrid seaborn theme in the ``paper`` context, then overrides
    rcParams to bind fonts, sizes, spines, ticks, and grid appearance to the
    tokens defined in this module.
    """
    sns.set_theme(style="whitegrid", context="paper")
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": FONT_STACK,
            "axes.titlesize": TEXT_HEADER,
            "axes.labelsize": TEXT_BODY,
            "xtick.labelsize": TEXT_SMALL,
            "ytick.labelsize": TEXT_SMALL,
            "legend.fontsize": TEXT_SMALL,
            "legend.title_fontsize": TEXT_SMALL,
            "figure.titlesize": TEXT_HEADER,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "grid.color": GRID_COLOR,
            "grid.alpha": 0.6,
            "grid.linewidth": STROKE_THIN * 0.6,
            "lines.linewidth": STROKE_MEDIUM,
            "lines.markersize": 4.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


_HEX_RE = re.compile(r'rgb\("(#[0-9a-fA-F]{6,8})"\)')


def verify_palette_matches_typst(typst_path: Path) -> None:
    """Assert that hex tokens in ``style.typ`` match the constants here.

    Args:
        typst_path: Path to ``thesis/diagrams/_lib/style.typ``.

    Raises:
        AssertionError: If any expected hex value is missing from the typst
            file, signalling that the palette has drifted between repos.
    """
    text = typst_path.read_text()
    found = {m.lower() for m in _HEX_RE.findall(text)}
    expected = {
        INK,
        MUTED,
        PRIMARY,
        ACCENT,
        ACCENT_FILL,
        ENVELOPE_FILL,
        ENVELOPE_STROKE,
        *(fill for fill, _ in LAYER_ACCENTS if fill != SURFACE),
        *(stroke for _, stroke in LAYER_ACCENTS if stroke != MUTED),
    }
    missing = {h for h in expected if h.lower() not in found}
    assert not missing, (
        f"palette drift vs {typst_path}: python constants "
        f"not present in typst file: {sorted(missing)}"
    )
