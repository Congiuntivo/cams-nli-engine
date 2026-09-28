"""Snapshot test: render a fixture spec and diff against expected .tex."""

from pathlib import Path

from tables.render import render
from tables.spec import load_spec

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
