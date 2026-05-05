from __future__ import annotations

import importlib.resources
import re


def load_prompt(package: str, filename: str) -> str:
    """Load a prompt file and resolve ``{{inject: Name}}`` markers.

    Markers are replaced with the contents of the corresponding ``.md`` file
    from the ``injections/`` directory of the ``nli_engine.engine.prompts``
    package.

    Args:
        package: Dotted package name where the prompt file lives.
        filename: Prompt filename relative to the package root.

    Returns:
        Prompt text with all injection markers resolved.
    """
    ref = importlib.resources.files(package) / filename
    content = ref.read_text(encoding="utf-8")
    return _resolve_injections(content)


def _resolve_injections(content: str) -> str:
    """Replace ``{{inject: Name}}`` markers with the contents of injection files."""
    injections_root = (
        importlib.resources.files("nli_engine.engine.prompts") / "injections"
    )

    def _load(match: re.Match) -> str:
        name = match.group(1).strip()
        return (injections_root / f"{name}.md").read_text(encoding="utf-8")

    return re.sub(r"\{\{inject:\s*(\w+)\s*\}\}", _load, content)
