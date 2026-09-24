"""Regenerate every LaTeX table fragment from its YAML spec."""

from __future__ import annotations

import sys
from pathlib import Path

from .render import render
from .spec import load_spec

ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = Path(__file__).resolve().parent / "specs"
OUT_DIR = Path(__file__).resolve().parent


def main() -> int:
    """Render every spec in ``tables/specs/`` to ``tables/<name>.tex``."""
    specs = sorted(SPECS_DIR.glob("*.yaml"))
    if not specs:
        print("no specs found in tables/specs/", file=sys.stderr)
        return 1
    for spec_path in specs:
        spec = load_spec(spec_path, ROOT)
        try:
            tex = render(spec, ROOT)
        except Exception as e:
            print(f"error rendering {spec_path.name}: {e}", file=sys.stderr)
            return 1
        out = OUT_DIR / f"{spec.name}.tex"
        out.write_text(tex)
        print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
