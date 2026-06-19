from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    """A single result returned by a retrieval query.

    Attributes:
        content: The text content of the chunk.
        score: Relevance score; higher means more relevant.
        source: Identifier of the originating document or chunk, used for
            debugging and evaluation tracing.
    """

    content: str
    score: float
    source: str


def format_chunks(chunks: list[RetrievedChunk]) -> str:
    """Format retrieved chunks as a source-annotated block for prompt injection.

    Uses Anthropic's recommended ``<context><document source="...">...</document></context>``
    layout. Shared by the warm initial injection in ``LLMStep`` and the on-demand
    ``retrieve_docs`` tool so the model sees a single consistent format.
    """
    return (
        "<context>\n"
        + "\n".join(
            f'<document source="{c.source}">\n{c.content}</document>' for c in chunks
        )
        + "\n</context>"
    )
