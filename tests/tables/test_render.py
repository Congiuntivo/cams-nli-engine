"""Snapshot test: render a fixture spec and diff against expected .tex."""

from pathlib import Path

from tables.render import render
from tables.spec import load_spec

FIXTURES = Path(__file__).parent / "fixtures"


def test_render_snapshot():
    """Rendered output must match the pinned expected.tex byte-for-byte."""
    spec = load_spec(FIXTURES / "spec.yaml", root=FIXTURES)
    actual = render(spec, root=FIXTURES)
    expected = (FIXTURES / "expected.tex").read_text()
    assert actual == expected
