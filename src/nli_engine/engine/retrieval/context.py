from __future__ import annotations

from pydantic import Field

from nli_engine.engine.retrieval.chunk import RetrievedChunk
from nli_engine.engine.workflow.base import WorkflowContext


class RetrievalContext(WorkflowContext):
    """Workflow context base class that carries retrieval results.

    Workflows that use a ``RetrievalStep`` should inherit from this instead of
    ``WorkflowContext`` directly. The ``retrieved_chunks`` field is populated by
    the step and exposed as the ``retrieved_context`` template variable so any
    downstream ``LLMStep`` can inject it via ``{{var: retrieved_context}}``.

    Attributes:
        retrieved_chunks: Chunks written by the most recent ``RetrievalStep``
            run. Empty until retrieval has been executed.
    """

    retrieved_chunks: list[RetrievedChunk] = Field(default_factory=list)

    def context_variables(self) -> dict[str, str]:
        """Expose retrieved chunks as the ``retrieved_context`` template variable.

        Returns:
            Mapping with a single key ``"retrieved_context"`` whose value is
            an empty string when no chunks are present, or a formatted block
            listing each chunk with its source and score.
        """
        if not self.retrieved_chunks:
            return {"retrieved_context": ""}
        formatted = "\n\n".join(
            f"[{chunk.source}] (score: {chunk.score:.2f})\n{chunk.content}"
            for chunk in self.retrieved_chunks
        )
        return {"retrieved_context": formatted}
