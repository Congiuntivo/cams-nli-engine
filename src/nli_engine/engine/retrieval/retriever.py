from __future__ import annotations

from abc import ABC, abstractmethod

from nli_engine.engine.retrieval.chunk import RetrievedChunk


class Retriever(ABC):
    """Abstract retrieval backend.

    Implementations may use any strategy — keyword matching, vector search,
    hybrid ranking, or a static lookup — as long as they satisfy this interface.
    """

    @abstractmethod
    def retrieve(
        self, query: str, top_k: int = 5, min_score: float = 0.0
    ) -> list[RetrievedChunk]:
        """Retrieve the most relevant chunks for a query.

        Args:
            query: Free-text search query.
            top_k: Maximum number of chunks to return.
            min_score: Drop chunks whose relevance score is strictly below this
                threshold. Defaults to ``0.0`` (no filtering). The meaningful
                range depends on the backend's scoring method.

        Returns:
            Up to ``top_k`` chunks scoring at least ``min_score``, ordered by
            descending relevance score.
        """
        ...
