from __future__ import annotations

import logging

from nli_engine.cli.logging.console import TraceHandler, configure_verbose_logging
from nli_engine.cli.logging.file import FileTraceHandler, configure_file_logging

_TRACE_LOGGERS: tuple[str, ...] = (
    "nli_engine.session",
    "nli_engine.step",
    "nli_engine.llm",
)


def initialize_trace_loggers() -> None:
    """Set all trace loggers to DEBUG and disable propagation to the root logger.

    Must be called before attaching any console or file handlers so that the
    logger level is never a bottleneck regardless of which handlers are active.
    Each handler is responsible for filtering at its own level.
    """
    for name in _TRACE_LOGGERS:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False


__all__ = [
    "FileTraceHandler",
    "TraceHandler",
    "configure_file_logging",
    "configure_verbose_logging",
    "initialize_trace_loggers",
]
