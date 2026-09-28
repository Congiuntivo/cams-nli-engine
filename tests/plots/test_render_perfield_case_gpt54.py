from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pytest

from plots.render import render
from plots.spec import load_spec

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = REPO_ROOT / "plots" / "specs" / "perfield_case_gpt54.yaml"
LONG_CSV = REPO_ROOT / "study" / "preprocessed" / "eval_perfield_case_gpt54_long.csv"

EXPECTED_FIELDS = [
    "primaryDevices",
    "connectedDevices",
    "tasks",
    "triggers",
    "taskControls",
    "connections",
    "applicationData",
    "other",
]
EXPECTED_CASE_LABELS = ["Case 001", "Case 002", "Case 003"]


def test_perfield_case_gpt54_renders(tmp_path: Path) -> None:
    if not LONG_CSV.exists():
        pytest.skip(f"preprocessed CSV missing at {LONG_CSV}")

    spec = load_spec(SPEC_PATH, REPO_ROOT)
    fig = render(spec, REPO_ROOT)

    assert len(fig.axes) == 1
    ax = fig.axes[0]

    tick_labels = [t.get_text() for t in ax.get_xticklabels()]
    assert tick_labels == EXPECTED_FIELDS

    lo, hi = ax.get_ylim()
    assert lo == 0.0 and hi == pytest.approx(1.05)

    legend = fig.legends[0]
    legend_texts = [t.get_text() for t in legend.get_texts()]
    for label in EXPECTED_CASE_LABELS:
        assert label in legend_texts
    assert "±1 SD" in legend_texts

    out = tmp_path / "out.pdf"
    fig.savefig(out, format="pdf", bbox_inches="tight")
    plt.close(fig)
    assert out.exists()
    assert out.stat().st_size > 1024
