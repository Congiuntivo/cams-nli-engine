"""Source registry: one entry per JSONL log corpus to preprocess.

Each :class:`Source` knows where its logs live and how to parse their
filenames back into (model, case_id, prompt_key, run) tuples. The filename
patterns differ slightly between corpora because the ReAct baseline prefixes
the model with ``react-baseline_``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Source:
    """One JSONL corpus to be preprocessed.

    Attributes:
        name: Short identifier used as the ``source`` column value.
        results_dir: Absolute path to the directory that contains the
            ``*.jsonl`` logs.
        filename_regex: Compiled regex matched against the file stem. Must
            expose named groups ``model``, ``case_id``, ``prompt``, ``run``.
        react_style_protocol: Whether ``turn_result.protocol`` is nested as
            ``{"protocol": {...}}`` (ReAct baseline) rather than the flat
            authoring-server dict.
    """

    name: str
    results_dir: Path
    filename_regex: re.Pattern[str]
    react_style_protocol: bool = False


_MAIN_RE = re.compile(
    r"^(?P<model>.+?)_(?P<case_id>\d{3}_[a-z_]+?)"
    r"_(?P<prompt>poor|medium|rich)_run(?P<run>\d+)$"
)

_REACT_RE = re.compile(
    r"^react-baseline_(?P<model>.+?)_(?P<case_id>\d{3}_[a-z_]+?)"
    r"_(?P<prompt>poor|medium|rich)_run(?P<run>\d+)$"
)


SOURCES: list[Source] = [
    Source(
        name="models",
        results_dir=REPO_ROOT / "study" / "runs" / "models" / "results",
        filename_regex=_MAIN_RE,
    ),
    Source(
        name="local_models",
        results_dir=REPO_ROOT / "study" / "runs" / "local_models" / "results",
        filename_regex=_MAIN_RE,
    ),
    Source(
        name="react_baseline",
        results_dir=REPO_ROOT / "study" / "baselines" / "react-baseline" / "results",
        filename_regex=_REACT_RE,
        react_style_protocol=True,
    ),
    # Placeholder — flip the results_dir once the noRAG runs land.
    Source(
        name="norag",
        results_dir=REPO_ROOT / "study" / "runs" / "norag" / "results",
        filename_regex=_MAIN_RE,
    ),
]

SOURCES_BY_NAME: dict[str, Source] = {s.name: s for s in SOURCES}
