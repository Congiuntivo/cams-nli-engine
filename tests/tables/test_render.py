"""Snapshot test: render a fixture spec and diff against expected .tex."""

from pathlib import Path

from tables.render import fmt_cell, highlighted_indices, render
from tables.spec import ColumnSpec, load_spec

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[2]
SPECS_DIR = ROOT / "tables" / "specs"


def test_render_snapshot():
    """Rendered output must match the pinned expected.tex byte-for-byte."""
    spec = load_spec(FIXTURES / "spec.yaml", root=FIXTURES)
    actual = render(spec, root=FIXTURES)
    expected = (FIXTURES / "expected.tex").read_text()
    assert actual == expected


def test_eval_quality_snapshot():
    """``eval_quality.yaml`` must render to the pinned fixture."""
    spec = load_spec(SPECS_DIR / "eval_quality.yaml", root=ROOT)
    actual = render(spec, root=ROOT)
    expected = (FIXTURES / "eval_quality_expected.tex").read_text()
    assert actual == expected


def test_eval_perfield_tier_snapshot():
    """``eval_perfield_tier.yaml`` must render to the pinned fixture."""
    spec = load_spec(SPECS_DIR / "eval_perfield_tier.yaml", root=ROOT)
    actual = render(spec, root=ROOT)
    expected = (FIXTURES / "eval_perfield_tier_expected.tex").read_text()
    assert actual == expected


def test_eval_baseline_summary_snapshot():
    """``eval_baseline_summary.yaml`` must render to the pinned fixture."""
    spec = load_spec(SPECS_DIR / "eval_baseline_summary.yaml", root=ROOT)
    actual = render(spec, root=ROOT)
    expected = (FIXTURES / "eval_baseline_summary_expected.tex").read_text()
    assert actual == expected


def test_eval_baseline_cells_snapshot():
    """``eval_baseline_cells.yaml`` must render to the pinned fixture."""
    spec = load_spec(SPECS_DIR / "eval_baseline_cells.yaml", root=ROOT)
    actual = render(spec, root=ROOT)
    expected = (FIXTURES / "eval_baseline_cells_expected.tex").read_text()
    assert actual == expected


def test_eval_execution_snapshot():
    """``eval_execution.yaml`` must render to the pinned fixture."""
    spec = load_spec(SPECS_DIR / "eval_execution.yaml", root=ROOT)
    actual = render(spec, root=ROOT)
    expected = (FIXTURES / "eval_execution_expected.tex").read_text()
    assert actual == expected


def test_eval_norag_summary_snapshot():
    """``eval_norag_summary.yaml`` must render to the pinned fixture."""
    spec = load_spec(SPECS_DIR / "eval_norag_summary.yaml", root=ROOT)
    actual = render(spec, root=ROOT)
    expected = (FIXTURES / "eval_norag_summary_expected.tex").read_text()
    assert actual == expected


def test_eval_norag_cells_snapshot():
    """``eval_norag_cells.yaml`` must render to the pinned fixture."""
    spec = load_spec(SPECS_DIR / "eval_norag_cells.yaml", root=ROOT)
    actual = render(spec, root=ROOT)
    expected = (FIXTURES / "eval_norag_cells_expected.tex").read_text()
    assert actual == expected


def test_experts_scratch_snapshot():
    """``experts_scratch.yaml`` must render to the pinned fixture."""
    spec = load_spec(SPECS_DIR / "experts_scratch.yaml", root=ROOT)
    actual = render(spec, root=ROOT)
    expected = (FIXTURES / "experts_scratch_expected.tex").read_text()
    assert actual == expected


def test_eval_human_headline_snapshot():
    """``eval_human_headline.yaml`` must render to the pinned fixture."""
    spec = load_spec(SPECS_DIR / "eval_human_headline.yaml", root=ROOT)
    actual = render(spec, root=ROOT)
    expected = (FIXTURES / "eval_human_headline_expected.tex").read_text()
    assert actual == expected


def test_eval_human_perfield_snapshot():
    """``eval_human_perfield.yaml`` must render to the pinned fixture."""
    spec = load_spec(SPECS_DIR / "eval_human_perfield.yaml", root=ROOT)
    actual = render(spec, root=ROOT)
    expected = (FIXTURES / "eval_human_perfield_expected.tex").read_text()
    assert actual == expected


def test_sd_column_emits_uncertainty_notation():
    """``sd_column`` cells emit siunitx compact-uncertainty notation."""
    col = ColumnSpec(name="mu", header="", type="numeric", decimals=3, sd_column="sd")
    row = {"mu": "0.7841", "sd": "0.0984"}
    assert fmt_cell(row, col) == "0.784(098)"


def test_sd_column_highlight_uses_mean_only():
    """Highlight ranks rows by mean; sd is ignored in the comparison."""
    col = ColumnSpec(
        name="mu",
        header="",
        type="numeric",
        decimals=3,
        sd_column="sd",
        highlight="max",
    )
    rows = [
        {"mu": "0.500", "sd": "0.900"},
        {"mu": "0.800", "sd": "0.001"},
    ]
    assert highlighted_indices(col, rows) == {1}


def test_sd_column_no_bold_on_zero_max():
    """When every row's mean is 0.0 under ``highlight: max``, no row is bolded."""
    col = ColumnSpec(
        name="mu",
        header="",
        type="numeric",
        decimals=3,
        sd_column="sd",
        highlight="max",
    )
    rows = [
        {"mu": "0.0", "sd": "0.0"},
        {"mu": "0.0", "sd": "0.0"},
    ]
    assert highlighted_indices(col, rows) == set()
