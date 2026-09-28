from __future__ import annotations

from pathlib import Path

import pytest

from plots.style import verify_palette_matches_typst

REPO_ROOT = Path(__file__).resolve().parents[2]
TYPST_PATH = REPO_ROOT.parent / "thesis" / "diagrams" / "_lib" / "style.typ"


def test_palette_matches_typst() -> None:
    if not TYPST_PATH.exists():
        pytest.skip(f"sibling thesis repo not present at {TYPST_PATH}")
    verify_palette_matches_typst(TYPST_PATH)
