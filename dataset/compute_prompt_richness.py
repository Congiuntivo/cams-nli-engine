"""Compute per-prompt richness metrics for the evaluation dataset."""

from __future__ import annotations

import csv
import re
import string
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

import textstat  # noqa: E402
import yaml  # noqa: E402
from lexical_diversity import lex_div as ld  # noqa: E402

MANIFEST = Path(__file__).parent / "manifest.yaml"
OUTPUT = Path(__file__).parent / "prompt_richness.csv"

HEADING_RE = re.compile(r"^#+ ")
BULLET_RE = re.compile(r"^\s*[-*] ")
TABLE_RE = re.compile(r"\|.*\|")
CAMEL_RE = re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b")
RICHNESS_ORDER = {"poor": 0, "medium": 1, "rich": 2}


def markdown_elements(text: str) -> int:
    headings = bullets = tables = 0
    for line in text.splitlines():
        if HEADING_RE.match(line):
            headings += 1
        if BULLET_RE.match(line):
            bullets += 1
        if TABLE_RE.search(line):
            tables += 1
    return headings + bullets + tables


def mtld_score(text: str) -> float:
    cleaned = text.lower().translate(str.maketrans("", "", string.punctuation))
    tokens = cleaned.split()
    return ld.mtld(tokens)


def main() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text())
    rows = []
    for case in manifest["cases"]:
        for richness, text in case["prompts"].items():
            rows.append(
                {
                    "case": case["id"],
                    "richness": richness,
                    "word_count": len(text.split()),
                    "markdown_elements": markdown_elements(text),
                    "carp_terms": len(CAMEL_RE.findall(text)),
                    "mtld": round(mtld_score(text), 2),
                    "fkgl": round(textstat.flesch_kincaid_grade(text), 2),
                }
            )
    rows.sort(key=lambda r: (r["case"], RICHNESS_ORDER[r["richness"]]))

    header = [
        "# MTLD reflects general lexical diversity and is not designed to track the case's rendering-formality axis; it is reported descriptively.",
        "# Flesch-Kincaid Grade Level assumes prose; markdown bullets and CamelCase identifiers inflate the score on rich prompts. Directional, not literal.",
    ]
    fieldnames = list(rows[0].keys())
    with OUTPUT.open("w", newline="") as fh:
        for line in header:
            fh.write(line + "\n")
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    sys.stdout.write(OUTPUT.read_text())


if __name__ == "__main__":
    main()
