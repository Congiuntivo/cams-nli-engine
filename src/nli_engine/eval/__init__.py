"""Evaluation module for NLI engine session logs.

Provides tools to parse JSONL session logs, compute execution metrics, and
compare protocol output against a ground-truth dataset.

Typical usage::

    from nli_engine.eval import parse_session, compute_metrics

    session = parse_session(Path("logs.jsonl"))
    metrics = compute_metrics(session)

For dataset evaluation::

    from nli_engine.eval import load_manifest, evaluate_dataset

    cases = load_manifest(Path("dataset/manifest.yaml"))
    results = evaluate_dataset(cases)
"""

from nli_engine.eval.comparison import compare_protocols
from nli_engine.eval.dataset import evaluate_dataset, load_manifest
from nli_engine.eval.metrics import compute_metrics
from nli_engine.eval.parser import parse_session

__all__ = [
    "parse_session",
    "compute_metrics",
    "compare_protocols",
    "load_manifest",
    "evaluate_dataset",
]
