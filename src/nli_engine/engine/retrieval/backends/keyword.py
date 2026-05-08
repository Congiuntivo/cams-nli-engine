from __future__ import annotations

from nli_engine.engine.retrieval.chunk import RetrievedChunk
from nli_engine.engine.retrieval.document import Document
from nli_engine.engine.retrieval.retriever import Retriever


class KeywordRetriever(Retriever):
    """In-memory keyword retriever.

    Scores each document by the fraction of query tokens that appear anywhere
    in its text (case-insensitive). Returns up to ``top_k`` chunks with a
    non-zero score, ordered by descending score.

    This backend requires no external dependencies and is suitable for small,
    static corpora and for testing retrieval pipelines without a vector store.

    Attributes:
        corpus: The indexed documents.
    """

    def __init__(self, corpus: list[Document]) -> None:
        """
        Args:
            corpus: Documents to search over.
        """
        self._corpus = corpus

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Return the top-k chunks whose text contains the most query tokens.

        Args:
            query: Free-text query; split on whitespace and lowercased before matching.
            top_k: Maximum number of results to return.

        Returns:
            Up to ``top_k`` chunks with score > 0, sorted by descending score.
            Returns an empty list when the query is blank or no document matches.
        """
        tokens = set(query.lower().split())
        if not tokens:
            return []

        scored: list[RetrievedChunk] = []
        for doc in self._corpus:
            content_lower = doc.content.lower()
            hits = sum(1 for token in tokens if token in content_lower)
            if hits:
                scored.append(
                    RetrievedChunk(doc.content, hits / len(tokens), doc.source)
                )

        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:top_k]
