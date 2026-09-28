"""Preprocess raw JSONL session logs into flat tables for analysis.

Public API:
    * :data:`SOURCES` / :func:`get_source` — the four corpora.
    * :func:`process_source` — extract one corpus into row lists.
    * :func:`write_tables` — dump combined rows to CSVs + JSON.
"""

from .extract import process_source
from .sources import SOURCES, SOURCES_BY_NAME, Source
from .writer import write_tables


def get_source(name: str) -> Source:
    """Return the :class:`Source` registered under *name*."""
    return SOURCES_BY_NAME[name]


__all__ = [
    "SOURCES",
    "SOURCES_BY_NAME",
    "Source",
    "get_source",
    "process_source",
    "write_tables",
]
