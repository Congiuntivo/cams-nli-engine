"""Evaluation module for NLI engine session logs.

Provides tools to parse JSONL session logs, compute execution metrics, and
compare protocol output against a ground-truth dataset.

Typical usage::

    from nli_engine.eval import parse_session, compute_metrics

    session = parse_session(Path("logs.jsonl"))
    metrics = compute_metrics(session)

For dataset evaluation::

    from nli_engine.eval import load_manifest, evaluate_dataset, resolve_last_from

    cases = load_manifest(Path("dataset/manifest.yaml"))
    resolved = resolve_last_from(cases, Path("logs/"))
    results = evaluate_dataset(resolved)
"""

from nli_engine.eval.io.dataset import (
    CaseResult,
    DatasetCase,
    ResolvedCase,
    evaluate_dataset,
    load_manifest,
    resolve_from_log,
    resolve_last_from,
)
from nli_engine.eval.io.parser import parse_session
from nli_engine.eval.scoring.comparison import ComparisonResult, compare_protocols
from nli_engine.eval.scoring.hashmatch import HashMatchScore
from nli_engine.eval.scoring.metrics import compute_metrics

__all__ = [
    "parse_session",
    "compute_metrics",
    "compare_protocols",
    "ComparisonResult",
    "HashMatchScore",
    "DatasetCase",
    "ResolvedCase",
    "CaseResult",
    "load_manifest",
    "evaluate_dataset",
    "resolve_last_from",
    "resolve_from_log",
]
