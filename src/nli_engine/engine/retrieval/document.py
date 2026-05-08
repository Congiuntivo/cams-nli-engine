from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class Document(BaseModel):
    """A single entry in a retrieval corpus.

    Attributes:
        source: Identifier for the originating document or section — used to
            populate ``RetrievedChunk.source`` and for debugging/eval tracing.
        content: The searchable text of this document.
    """

    source: str
    content: str
