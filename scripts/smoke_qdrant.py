"""Smoke test for QdrantRetriever.

Requires QDRANT_URL, QDRANT_COLLECTION set in .env and a populated collection.
Run download_models.py first if FastEmbed models are not yet cached.

Usage:
    uv run python scripts/smoke_qdrant.py [QUERY]
"""

import sys
from pathlib import Path

from nli_engine.engine.retrieval.backends.qdrant import QdrantRetriever
from nli_engine.engine.workflow.config import WorkflowConfig

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
DEFAULT_QUERY = "smartphone recording steps"


def main() -> None:
    """Load config, instantiate QdrantRetriever, run a query, and print results."""
    query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUERY
    config = WorkflowConfig.from_yaml(CONFIG_PATH)
    if config.retrieval is None:
        sys.exit("No retrieval config found in config.yaml")

    retriever = QdrantRetriever(
        dense_model=config.retrieval.dense_model,
        sparse_model=config.retrieval.sparse_model,
        multi_model=config.retrieval.multi_model,
        method=config.retrieval.method,
        rerank=config.retrieval.rerank,
        prefetch_limit=config.retrieval.prefetch_limit,
    )

    print(f"Query: {query!r}  (top_k={config.retrieval.top_k})")
    chunks = retriever.retrieve(query, top_k=config.retrieval.top_k)

    if not chunks:
        sys.exit("No results returned — is the collection populated?")

    for i, chunk in enumerate(chunks, 1):
        preview = chunk.content[:120].replace("\n", " ")
        print(f"\n[{i}] score={chunk.score:.4f}  source={chunk.source!r}")
        print(f"    {preview}...")


if __name__ == "__main__":
    main()
