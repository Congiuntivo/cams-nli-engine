from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator


class RetrievalConfig(BaseModel):
    """Configuration for the Qdrant retrieval backend.

    Attributes:
        dense_model: LiteLLM model string for dense embeddings.
        sparse_model: FastEmbed model name for BM25 sparse embeddings.
        multi_model: FastEmbed model name for ColBERT late-interaction embeddings.
        method: Search strategy — ``"hybrid"``, ``"dense"``, or ``"sparse"``.
        rerank: Apply ColBERT reranking over the hybrid prefetch. Only valid
            when ``method`` is ``"hybrid"``.
        prefetch_limit: Candidates fetched per branch before fusion or reranking.
        top_k: Final number of results returned.
        min_score: Drop chunks whose relevance score is strictly below this
            threshold. ``0.0`` disables filtering. Calibrate empirically from
            the per-chunk scores logged in ``StepLog.extra.chunks``.
    """

    dense_model: str
    sparse_model: str
    multi_model: str
    method: str = "hybrid"
    rerank: bool = True
    prefetch_limit: int = 50
    top_k: int = 5
    min_score: float = 0.0

    @model_validator(mode="after")
    def _rerank_requires_hybrid(self) -> RetrievalConfig:
        """Enforce that reranking is only enabled for hybrid search."""
        if self.rerank and self.method != "hybrid":
            raise ValueError("rerank=True requires method='hybrid'")
        return self


class WorkflowConfig(BaseModel):
    models: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping from model purpose name to model identifier.",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Additional parameters for the workflow."
    )
    max_iterations: dict[str, int] = Field(
        default_factory=dict,
        description="Mapping from step name to maximum number of iterations for that step.",
    )
    retrieval: RetrievalConfig | None = None

    @classmethod
    def from_yaml(cls, path: str | Path) -> WorkflowConfig:
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data or {})
