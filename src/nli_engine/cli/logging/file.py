from __future__ import annotations

import datetime
import json
import logging
from pathlib import Path

# Standard LogRecord attributes — everything else is considered an extra field
# added via the ``extra=`` parameter and gets written to the JSON log.
_STANDARD_LOG_FIELDS: frozenset[str] = frozenset(
    {
        "args",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "taskName",
        "thread",
        "threadName",
    }
)


class FileTraceHandler(logging.Handler):
    """Logging handler that writes structured trace events to a JSON Lines file.

    Each log record is serialised as a single JSON object on its own line,
    prefixed with an ISO-8601 UTC timestamp. Non-JSON-serialisable values are
    coerced to strings via ``json.dumps(default=str)``.

    Handles all events emitted by ``nli_engine.session``, ``nli_engine.step``,
    and ``nli_engine.llm`` loggers. The file is flushed after every record so
    the log is readable even if the process crashes mid-session.
    """

    def __init__(self, path: Path) -> None:
        """
        Args:
            path: Destination path. Can be a filename or a directory. If a directory is provided, a timestamped filename will be generated within it.
        """
        super().__init__(level=logging.DEBUG)
        if path.is_dir():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self._file_path = path / f"logs_{timestamp}.jsonl"
        else:
            self._file_path = path

        self._file = open(self._file_path, "w", encoding="utf-8")

    def emit(self, record: logging.LogRecord) -> None:
        try:
            extra = {
                k: v
                for k, v in record.__dict__.items()
                if k not in _STANDARD_LOG_FIELDS
            }
            ts = datetime.datetime.fromtimestamp(
                record.created, tz=datetime.timezone.utc
            ).isoformat()
            entry = {"ts": ts, **extra}
            self._file.write(json.dumps(entry, default=str) + "\n")
            self._file.flush()
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        """Flush and close the underlying file."""
        try:
            self._file.flush()
            self._file.close()
        finally:
            super().close()


def configure_file_logging(path: Path) -> None:
    """Attach a FileTraceHandler to all trace loggers and write a JSON Lines log.

    Subscribes to ``nli_engine.session``, ``nli_engine.step``, and
    ``nli_engine.llm`` so every event — including full LLM request/response
    blocks — is captured regardless of the console verbosity. Logger levels are
    managed externally by ``initialize_trace_loggers``; this function only
    registers the handler.

    Args:
        path: Destination ``.jsonl`` file path. Created or overwritten.
    """
    if not isinstance(path, Path):
        raise ValueError(f"Expected a `pathlib.Path` object, got {type(path)}")

    handler = FileTraceHandler(path)
    for name in ("nli_engine.session", "nli_engine.step", "nli_engine.llm"):
        logging.getLogger(name).addHandler(handler)
