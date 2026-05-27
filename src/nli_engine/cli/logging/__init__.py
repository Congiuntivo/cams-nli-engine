from __future__ import annotations

import logging
import sys

from nli_engine.cli.logging.console import TraceHandler, configure_verbose_logging
from nli_engine.cli.logging.file import FileTraceHandler, configure_file_logging

# Suppress botocore-absent WARNINGs emitted at LiteLLM import time.
# Fixed upstream in LiteLLM 1.87: https://github.com/BerriAI/litellm/issues/28175
logging.getLogger("LiteLLM").setLevel(logging.ERROR)

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

    A WARNING-level stderr handler is always attached so that warnings and
    errors from the engine are visible even when ``--verbose`` is not active.
    """
    warn_handler = logging.StreamHandler(sys.stderr)
    warn_handler.setLevel(logging.WARNING)
    warn_handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))

    for name in _TRACE_LOGGERS:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        logger.addHandler(warn_handler)


__all__ = [
    "FileTraceHandler",
    "TraceHandler",
    "configure_file_logging",
    "configure_verbose_logging",
    "initialize_trace_loggers",
]
