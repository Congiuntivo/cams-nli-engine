#!/usr/bin/env python3
"""Inline rich prompt markdown files into the dataset manifest.

For each file at ``dataset/prompts/<prefix>_<richness>.md``, this script writes
the file's contents under ``prompts.<richness>`` for the case in
``dataset/manifest.yaml`` whose ``id`` starts with ``<prefix>_``.

The value is emitted as a YAML literal block scalar (``|``) so newlines are
preserved exactly. (Double-quoted single-line scalars with ``\\n`` escapes are
not safe here: a YAML formatter may unfold them, after which YAML's folding
rules silently collapse single newlines into spaces and corrupt the content.)

Operates on the manifest as text so unrelated comments and key ordering are
preserved. Idempotent — existing ``richness`` keys (single-line or block) are
replaced wholesale.
"""

from __future__ import annotations

import re
from pathlib import Path

DATASET_DIR = Path(__file__).parent
MANIFEST_PATH = DATASET_DIR / "manifest.yaml"
PROMPTS_DIR = DATASET_DIR / "prompts"
PROMPT_INDENT = "      "  # 6 spaces — prompt keys live at this indent
BODY_INDENT = PROMPT_INDENT + "  "  # block-scalar body indent (2 deeper)


def _case_ids(text: str) -> list[str]:
    return re.findall(r'^  - id: "([^"]+)"', text, flags=re.MULTILINE)


def _format_body(content: str) -> list[str]:
    """Format ``content`` as the indented body lines of a ``|`` block scalar."""
    if not content.endswith("\n"):
        content += "\n"
    lines = content.split("\n")
    lines.pop()  # drop trailing empty from the final newline
    return [BODY_INDENT + line if line else "" for line in lines]


def _find_block_end(lines: list[str], start: int, key_indent_len: int) -> int:
    """Return the exclusive end index of the key block beginning at ``lines[start]``.

    A continuation line is one that is more deeply indented than the key, or a
    blank line that precedes another continuation line. Blank lines followed
    by a sibling key (or new section) belong to the parent, not the key.
    """
    i = start + 1
    while i < len(lines):
        line = lines[i].rstrip("\n")
        if line.strip() == "":
            j = i + 1
            while j < len(lines) and lines[j].rstrip("\n").strip() == "":
                j += 1
            if (
                j < len(lines)
                and (len(lines[j]) - len(lines[j].lstrip(" "))) > key_indent_len
            ):
                i = j
                continue
            break
        indent = len(line) - len(line.lstrip(" "))
        if indent > key_indent_len:
            i += 1
        else:
            break
    return i


def _splice_rich(text: str, case_id: str, richness: str, content: str) -> str:
    lines = text.splitlines(keepends=True)

    case_re = re.compile(rf'^  - id: "{re.escape(case_id)}"')
    case_start = next((i for i, ln in enumerate(lines) if case_re.match(ln)), None)
    if case_start is None:
        raise KeyError(f"case {case_id!r} not found")

    case_end = len(lines)
    for i in range(case_start + 1, len(lines)):
        if re.match(r'^  - id: "', lines[i]):
            case_end = i
            break

    prompts_idx = None
    for i in range(case_start + 1, case_end):
        if lines[i].rstrip("\n").strip() == "prompts:":
            prompts_idx = i
            break
    if prompts_idx is None:
        raise KeyError(f"case {case_id!r} has no `prompts:` section")

    key_re = re.compile(rf"^{re.escape(PROMPT_INDENT)}{re.escape(richness)}:")
    key_line_idx = next(
        (i for i in range(prompts_idx + 1, case_end) if key_re.match(lines[i])),
        None,
    )

    new_block = [
        f"{PROMPT_INDENT}{richness}: |-\n",
        *(ln + "\n" for ln in _format_body(content)),
    ]

    if key_line_idx is not None:
        block_end = _find_block_end(lines, key_line_idx, len(PROMPT_INDENT))
        new_lines = lines[:key_line_idx] + new_block + lines[block_end:]
    else:
        insert_at = case_end
        while insert_at > prompts_idx + 1 and lines[insert_at - 1].strip() == "":
            insert_at -= 1
        new_lines = lines[:insert_at] + new_block + lines[insert_at:]

    return "".join(new_lines)


def main() -> None:
    text = MANIFEST_PATH.read_text(encoding="utf-8")
    case_ids = _case_ids(text)

    for prompt_file in sorted(PROMPTS_DIR.glob("*.md")):
        prefix, _, richness = prompt_file.stem.rpartition("_")
        matches = [cid for cid in case_ids if cid.split("_", 1)[0] == prefix]
        if not matches:
            print(f"skip {prompt_file.name}: no case with prefix {prefix!r}")
            continue
        if len(matches) > 1:
            print(f"skip {prompt_file.name}: ambiguous prefix {prefix!r} ({matches})")
            continue
        content = prompt_file.read_text(encoding="utf-8")
        text = _splice_rich(text, matches[0], richness, content)
        print(f"ok   {prompt_file.name} -> {matches[0]}.prompts.{richness}")

    MANIFEST_PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
