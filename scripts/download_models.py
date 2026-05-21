"""Download FastEmbed models to FASTEMBED_CACHE_PATH.

Run once before starting the engine in a new environment:

    uv run python scripts/download_models.py
"""

import os
import sys

from fastembed import LateInteractionTextEmbedding, SparseTextEmbedding


def main() -> None:
    """Download sparse and multi-vector FastEmbed models to the configured cache directory."""
    cache_dir = os.environ.get("FASTEMBED_CACHE_PATH")
    if not cache_dir:
        sys.exit("FASTEMBED_CACHE_PATH is not set")

    print(f"Downloading models to {cache_dir} ...")
    SparseTextEmbedding("Qdrant/bm25", cache_dir=cache_dir)
    print("  sparse: Qdrant/bm25 done")
    LateInteractionTextEmbedding("colbert-ir/colbertv2.0", cache_dir=cache_dir)
    print("  multi:  colbert-ir/colbertv2.0 done")
    print("All models ready.")


if __name__ == "__main__":
    main()
