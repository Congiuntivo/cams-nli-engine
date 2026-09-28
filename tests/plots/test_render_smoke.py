from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pytest

from plots.render import render
from plots.spec import load_spec

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = REPO_ROOT / "plots" / "specs" / "richness_f1_small_multiples.yaml"
SUMMARY_PATH = REPO_ROOT / "study" / "runs" / "summary.csv"


def test_demo_spec_renders(tmp_path: Path) -> None:
    if not SUMMARY_PATH.exists():
        pytest.skip(f"summary CSV not present at {SUMMARY_PATH}")

    spec = load_spec(SPEC_PATH, REPO_ROOT)
    fig = render(spec, REPO_ROOT)

    assert len(fig.axes) == 3
    lo, hi = fig.axes[0].get_ylim()
    assert lo == 0.0 and hi > 1.0

    out = tmp_path / "out.pdf"
    fig.savefig(out, format="pdf", bbox_inches="tight")
    plt.close(fig)
    assert out.exists()
    assert out.stat().st_size > 1024
