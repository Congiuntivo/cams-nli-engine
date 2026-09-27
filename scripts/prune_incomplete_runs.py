"""Delete JSONL session logs that terminated before ``turn_result``.

Distinguishes two failure classes based on the last event in each file:

- ``error``: last event is ``llm_error`` or ``retrieval_error`` — the workflow
  raised an exception (Ollama down, model timed out, structured output
  malformed, unknown tool, etc.). These are typically worth deleting so the
  batch runner will regenerate them on the next invocation.
- ``truncated``: last event is anything else that isn't ``turn_result`` — the
  process was killed externally (Ctrl-C, OOM, quota / budget cutoff). Not
  necessarily worth deleting; the failure may have been intentional.

Complete files (last event is ``turn_result``) are always left alone.

Usage:
    uv run python scripts/prune_incomplete_runs.py                # dry-run report
    uv run python scripts/prune_incomplete_runs.py --delete       # delete errors
    uv run python scripts/prune_incomplete_runs.py --delete \\
        --kind error,truncated                                    # delete both
    uv run python scripts/prune_incomplete_runs.py \\
        --base study/baselines --delete                           # different root
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_ERROR_EVENTS = frozenset({"llm_error", "retrieval_error"})
_KIND_CHOICES = ("error", "truncated")
_REPO_ROOT = Path(__file__).resolve().parent.parent


def _last_event(path: Path) -> str | None:
    """Return the ``event`` field of the last JSON line, or ``None`` if empty."""
    last: str | None = None
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            event = obj.get("event")
            if event is not None:
                last = event
    return last


def _classify(path: Path) -> str:
    """Return ``"complete"``, ``"error"``, ``"truncated"``, or ``"empty"``."""
    last = _last_event(path)
    if last is None:
        return "empty"
    if last == "turn_result":
        return "complete"
    if last in _ERROR_EVENTS:
        return "error"
    return "truncated"


def _scan(base: Path) -> dict[str, list[Path]]:
    """Group every ``results/*.jsonl`` under ``base`` by classification."""
    buckets: dict[str, list[Path]] = {
        "complete": [],
        "error": [],
        "truncated": [],
        "empty": [],
    }
    for path in sorted(base.glob("*/results/*.jsonl")):
        buckets[_classify(path)].append(path)
    return buckets


def _print_report(buckets: dict[str, list[Path]]) -> None:
    total = sum(len(v) for v in buckets.values())
    print(f"Scanned {total} log(s):")
    for kind in ("complete", "error", "truncated", "empty"):
        print(f"  {kind:>10}: {len(buckets[kind])}")

    # Group incomplete files by their run-directory for a compact preview.
    for kind in ("error", "truncated", "empty"):
        if not buckets[kind]:
            continue
        print(f"\n[{kind}]")
        counts = Counter(p.parent.parent.name for p in buckets[kind])
        for source, n in counts.most_common():
            print(f"  {source}: {n}")


def main() -> int:
    """Parse arguments, scan the tree, and optionally delete matching files."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--base",
        default=str(_REPO_ROOT / "study" / "runs"),
        help="Root dir. Files matched: <base>/*/results/*.jsonl. Default: study/runs.",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete matching files. Without this flag the script only reports.",
    )
    parser.add_argument(
        "--kind",
        default="error",
        help=(
            "Comma-separated categories to act on: "
            f"any of {'|'.join(_KIND_CHOICES)}. Default: 'error'."
        ),
    )
    args = parser.parse_args()

    kinds = [k.strip() for k in args.kind.split(",") if k.strip()]
    invalid = [k for k in kinds if k not in _KIND_CHOICES]
    if invalid:
        print(
            f"Unknown kind(s): {invalid}. Valid: {list(_KIND_CHOICES)}",
            file=sys.stderr,
        )
        return 2

    base = Path(args.base)
    if not base.is_dir():
        print(f"Base dir does not exist: {base}", file=sys.stderr)
        return 2

    buckets = _scan(base)
    _print_report(buckets)

    victims = [p for k in kinds for p in buckets[k]]
    if not victims:
        print(f"\nNo logs match kinds={kinds}. Nothing to do.")
        return 0

    print(f"\nMatched {len(victims)} log(s) in kinds={kinds}:")
    for p in victims:
        print(f"  {p.relative_to(_REPO_ROOT)}")

    if not args.delete:
        print("\n(dry run) Pass --delete to remove these files.")
        return 0

    for p in victims:
        p.unlink()
    print(f"\nDeleted {len(victims)} log(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
