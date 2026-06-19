from __future__ import annotations

from pydantic import BaseModel, Field

from nli_engine.engine.retrieval.chunk import format_chunks
from nli_engine.engine.retrieval.retriever import Retriever
from nli_engine.engine.tools import BoundTool


class RetrievalRequest(BaseModel):
    """Request model for the retrieve_docs tool.

    Attributes:
        query: Focused search query targeting the specific CARP concept,
            API, or term the caller needs documentation for.
    """

    query: str = Field(
        description=(
            "Focused search query for the CARP documentation corpus. Use "
            "concrete CARP terminology (e.g. 'BackgroundTask measures', "
            "'PeriodicTrigger', 'data endpoint'). Keep it concise."
        )
    )


def build_retrieve_docs_tool(
    retriever: Retriever,
    top_k: int,
    min_score: float,
) -> BoundTool:
    """Wrap a Retriever as a BoundTool callable by an LLM step.

    The returned tool lets the model fetch additional documentation on demand
    during a multi-iteration step — addressing the stale-context problem where
    a single retrieval at iteration 0 can't keep up with how the conversation
    evolves over 20-40 LLM calls.

    Args:
        top_k: Maximum chunks per call. Locked at tool construction time.
        min_score: Drop chunks below this score. Locked at tool construction time.

    Returns:
        BoundTool with name ``retrieve_docs`` accepting a ``RetrievalRequest``.
    """

    def _call(req: RetrievalRequest) -> str:
        chunks = retriever.retrieve(req.query, top_k, min_score)
        if not chunks:
            return "No relevant documents found for this query."
        return format_chunks(chunks)

    return BoundTool(
        name="retrieve_docs",
        description=(
            "Search the CARP documentation corpus for chunks relevant to a "
            "focused query. Call when you need additional reference material "
            "beyond what is already in your context — for example, when an "
            "API name, parameter, or concept comes up that you are unsure about."
        ),
        request_model=RetrievalRequest,
        call=_call,
    )
