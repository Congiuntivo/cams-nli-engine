"""Dense-only retrieval MCP server for the ReAct baseline.

Wraps the engine's :class:`~nli_engine.engine.retrieval.backends.qdrant.QdrantRetriever`
in ``method="dense"`` mode and exposes a single ``search_docs`` tool over stdio.

The off-the-shelf ``qdrant/mcp-server-qdrant`` cannot query the engine's
collection because that collection stores three named vectors (``dense``,
``sparse``, ``multi``) whereas the reference server assumes a single unnamed
vector. This tiny wrapper reuses the engine's own retriever code, so the
embedder and the named-vector plumbing are guaranteed to match the collection.
"""

from __future__ import annotations

from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from nli_engine.engine.retrieval.backends.qdrant import QdrantRetriever

_RETRIEVER: QdrantRetriever | None = None


def _retriever() -> QdrantRetriever:
    global _RETRIEVER
    if _RETRIEVER is None:
        _RETRIEVER = QdrantRetriever(
            dense_model="ollama/mahonzhan/all-MiniLM-L6-v2",
            sparse_model="Qdrant/bm25",
            multi_model="colbert-ir/colbertv2.0",
            method="dense",
            rerank=False,
        )
    return _RETRIEVER


mcp = FastMCP(name="react-baseline-retrieval")


@mcp.tool()
def search_docs(
    query: Annotated[str, Field(description="Free-text query about CAMS.")],
    top_k: Annotated[int, Field(description="Max chunks to return.", ge=1, le=20)] = 5,
) -> list[dict]:
    """Search the CAMS documentation collection for relevant chunks.

    Args:
        query: Free-text search query.
        top_k: Maximum number of chunks to return.

    Returns:
        List of ``{content, source, score}`` dicts, ordered by descending
        relevance.
    """
    chunks = _retriever().retrieve(query=query, top_k=top_k, min_score=0.0)
    return [
        {"content": c.content, "source": c.source, "score": float(c.score)}
        for c in chunks
    ]


def main() -> None:
    """Run the stdio MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
