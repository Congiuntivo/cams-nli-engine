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
