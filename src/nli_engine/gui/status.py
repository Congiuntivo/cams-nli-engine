"""Logging handler that surfaces workflow step starts to the GUI."""

from __future__ import annotations

import logging
from typing import Callable

from nli_engine.gui.labels import friendly

_STEP_LOGGER_NAME = "nli_engine.step"


class StatusHandler(logging.Handler):
    """Forward ``step_begin`` events on ``nli_engine.step`` to a callback as friendly labels.

    Other events emitted on the step logger are ignored. The callback is
    invoked from whichever thread emitted the log record, so it must be
    thread-safe; the GUI uses a small mutable holder polled by a UI timer.
    """

    def __init__(self, on_status: Callable[[str], None]) -> None:
        """
        Args:
            on_status: Called with the friendly label each time a step starts.
        """
        super().__init__(level=logging.INFO)
        self._on_status = on_status

    def emit(self, record: logging.LogRecord) -> None:
        if getattr(record, "event", None) != "step_begin":
            return
        step_name = getattr(record, "step_name", "?")
        try:
            self._on_status(friendly(step_name))
        except Exception:
            self.handleError(record)


def attach(on_status: Callable[[str], None]) -> StatusHandler:
    """Attach a StatusHandler to ``nli_engine.step`` and return it for later detach."""
    handler = StatusHandler(on_status)
    logging.getLogger(_STEP_LOGGER_NAME).addHandler(handler)
    return handler


def detach(handler: StatusHandler) -> None:
    """Remove a previously attached StatusHandler from ``nli_engine.step``."""
    logging.getLogger(_STEP_LOGGER_NAME).removeHandler(handler)
