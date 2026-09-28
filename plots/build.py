"""Regenerate every plot PDF from its YAML spec."""

from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from .render import render
from .spec import load_spec

_FIXED_CREATION_DATE = _dt.datetime(2026, 1, 1, tzinfo=_dt.timezone.utc)

ROOT = Path(__file__).resolve().parent.parent
SPECS_DIR = Path(__file__).resolve().parent / "specs"
OUT_DIR = Path(__file__).resolve().parent


def main() -> int:
    """Render every spec in ``plots/specs/`` to ``plots/<name>.pdf``."""
    specs = sorted(SPECS_DIR.glob("*.yaml"))
    if not specs:
        print("no specs found in plots/specs/", file=sys.stderr)
        return 1
    for spec_path in specs:
        spec = load_spec(spec_path, ROOT)
        try:
            fig = render(spec, ROOT)
        except Exception as e:
            print(f"error rendering {spec_path.name}: {e}", file=sys.stderr)
            return 1
        out = OUT_DIR / f"{spec.name}.pdf"
        source_rel = (
            spec.source.relative_to(ROOT)
            if spec.source.is_relative_to(ROOT)
            else spec.source
        )
        fig.savefig(
            out,
            format="pdf",
            bbox_inches="tight",
            metadata={
                "Creator": "plots/build.py",
                "Title": spec.name,
                "Subject": f"AUTO-GENERATED from {source_rel} -- do not edit by hand.",
                "CreationDate": _FIXED_CREATION_DATE,
            },
        )
        plt.close(fig)
        print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
