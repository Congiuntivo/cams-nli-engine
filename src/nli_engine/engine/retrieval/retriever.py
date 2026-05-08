from __future__ import annotations

from abc import ABC, abstractmethod

from nli_engine.engine.retrieval.chunk import RetrievedChunk


class Retriever(ABC):
    """Abstract retrieval backend.

    Implementations may use any strategy — keyword matching, vector search,
    hybrid ranking, or a static lookup — as long as they satisfy this interface.
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Retrieve the most relevant chunks for a query.

        Args:
            query: Free-text search query.
            top_k: Maximum number of chunks to return.

        Returns:
            Up to ``top_k`` chunks ordered by descending relevance score.
        """
        ...
