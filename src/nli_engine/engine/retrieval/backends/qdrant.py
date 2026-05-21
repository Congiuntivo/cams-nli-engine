from __future__ import annotations

import os

import litellm
from fastembed import LateInteractionTextEmbedding, SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Fusion, FusionQuery, Prefetch, SparseVector

from nli_engine.engine.retrieval.chunk import RetrievedChunk
from nli_engine.engine.retrieval.retriever import Retriever


class QdrantRetriever(Retriever):
    """Hybrid retrieval backend backed by a Qdrant collection.

    Dense embeddings are produced via LiteLLM (e.g. an Ollama-hosted model).
    Sparse (BM25) and multi-vector (ColBERT) embeddings are produced via
    FastEmbed, loaded from the ``FASTEMBED_CACHE_PATH`` environment variable.

    Deployment parameters are read from the environment:
    - ``QDRANT_URL`` — Qdrant instance URL (required)
    - ``QDRANT_COLLECTION`` — collection name to query (required)
    - ``FASTEMBED_CACHE_PATH`` — path to pre-downloaded FastEmbed models (optional)
    - ``OPENAI_API_BASE`` — override LiteLLM endpoint when needed (optional)

    Attributes:
        Configured at construction time; no public attributes.
    """

    def __init__(
        self,
        dense_model: str,
        sparse_model: str,
        multi_model: str,
        method: str = "hybrid",
        rerank: bool = True,
        prefetch_limit: int = 50,
    ) -> None:
        """Initialise the retriever and load FastEmbed models into memory.

        Args:
            dense_model: LiteLLM model string used for dense embeddings.
            sparse_model: FastEmbed model name for BM25 sparse embeddings.
            multi_model: FastEmbed model name for ColBERT late-interaction embeddings.
            method: Search strategy — ``"hybrid"``, ``"dense"``, or ``"sparse"``.
            rerank: Apply ColBERT reranking over the hybrid prefetch. Only valid
                when ``method`` is ``"hybrid"``.
            prefetch_limit: Candidates fetched per branch before fusion or reranking.
        """
        self._client = QdrantClient(url=os.environ["QDRANT_URL"])
        self._collection = os.environ["QDRANT_COLLECTION"]
        self._dense_model = dense_model
        self._method = method
        self._rerank = rerank
        self._prefetch_limit = prefetch_limit

        cache = os.environ.get("FASTEMBED_CACHE_PATH")
        self._sparse_enc = SparseTextEmbedding(sparse_model, cache_dir=cache)
        self._multi_enc = LateInteractionTextEmbedding(multi_model, cache_dir=cache)

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        """Retrieve the most relevant chunks for a query.

        Args:
            query: Free-text search query.
            top_k: Maximum number of chunks to return.

        Returns:
            Up to ``top_k`` chunks ordered by descending relevance score.
        """
        dense = self._embed_dense(query)
        sparse = self._embed_sparse(query)
        multi = self._embed_multi(query)

        kwargs = self._build_query_kwargs(dense, sparse, multi, top_k)
        points = self._client.query_points(
            collection_name=self._collection, **kwargs
        ).points

        return [
            RetrievedChunk(
                content=p.payload["text"],
                score=p.score,
                source=p.payload.get("source_name", ""),
            )
            for p in points
        ]

    def _embed_dense(self, text: str) -> list[float]:
        """Embed text with the dense LiteLLM model."""
        response = litellm.embedding(model=self._dense_model, input=[text])
        return response.data[0]["embedding"]

    def _embed_sparse(self, text: str) -> SparseVector:
        """Embed text as a BM25 sparse vector."""
        result = next(self._sparse_enc.embed([text]))
        return SparseVector(
            indices=result.indices.tolist(), values=result.values.tolist()
        )

    def _embed_multi(self, text: str) -> list[list[float]]:
        """Embed text as ColBERT token-level multi-vectors."""
        result = next(self._multi_enc.query_embed([text]))
        return result.tolist()

    def _build_query_kwargs(
        self,
        dense: list[float],
        sparse: SparseVector,
        multi: list[list[float]],
        top_k: int,
    ) -> dict:
        """Build Qdrant query_points kwargs for the configured search method."""
        if self._method == "dense":
            return {"query": dense, "using": "dense", "limit": top_k}
        if self._method == "sparse":
            return {"query": sparse, "using": "sparse", "limit": top_k}
        prefetch = [
            Prefetch(query=dense, using="dense", limit=self._prefetch_limit),
            Prefetch(query=sparse, using="sparse", limit=self._prefetch_limit),
        ]
        if self._rerank:
            return {
                "prefetch": prefetch,
                "query": multi,
                "using": "multi",
                "limit": top_k,
            }
        return {
            "prefetch": prefetch,
            "query": FusionQuery(fusion=Fusion.RRF),
            "limit": top_k,
        }
