from __future__ import annotations

import time

from nli_engine.engine.retrieval.chunk import RetrievedChunk
from nli_engine.engine.retrieval.context import RetrievalContext
from nli_engine.engine.retrieval.query import LastUserMessageExtractor, QueryExtractor
from nli_engine.engine.retrieval.retriever import Retriever
from nli_engine.engine.tools import BoundTool
from nli_engine.engine.workflow.base import Step, WorkflowContext
from nli_engine.engine.workflow.log import StepLog


class RetrievalStep(Step):
    """Workflow step that retrieves relevant chunks and writes them to the context.

    Extracts a query from the current context using a ``QueryExtractor``, passes
    it to a ``Retriever``, and stores the results in
    ``context.retrieved_chunks``. The context must be an instance of
    ``RetrievalContext`` (or a subclass); a ``TypeError`` is raised immediately
    if it is not.

    Downstream ``LLMStep`` instances can inject the retrieved text into their
    system prompts via the ``{{var: retrieved_context}}`` tag.
    """

    def __init__(
        self,
        name: str,
        retriever: Retriever,
        query_extractor: QueryExtractor | None = None,
        top_k: int = 5,
    ) -> None:
        """
        Args:
            name: Step name; appears in ``StepLog``.
            retriever: Backend used to fetch relevant chunks.
            query_extractor: Strategy for deriving the search query from context.
                Defaults to ``LastUserMessageExtractor`` when ``None``.
            top_k: Maximum number of chunks to retrieve.
        """
        super().__init__(name, tool_names=[])
        self._retriever = retriever
        self._query_extractor: QueryExtractor = (
            query_extractor
            if query_extractor is not None
            else LastUserMessageExtractor()
        )
        self._top_k = top_k

    def _run(
        self, context: WorkflowContext, tools: list[BoundTool]
    ) -> tuple[list[RetrievedChunk], StepLog]:
        """Execute retrieval and store the results in context.

        Args:
            context: Must be a ``RetrievalContext`` instance.
            tools: Unused; ``RetrievalStep`` calls no LLM tools.

        Returns:
            A tuple of the retrieved chunks and a ``StepLog`` containing
            the query and chunk count in its ``extra`` field.

        Raises:
            TypeError: If ``context`` is not an instance of ``RetrievalContext``.
        """
        if not isinstance(context, RetrievalContext):
            raise TypeError(
                f"RetrievalStep '{self.name}' requires a RetrievalContext but received "
                f"{type(context).__name__}. Make your WorkflowContext subclass extend "
                "RetrievalContext."
            )
        start = time.monotonic()
        query = self._query_extractor.extract(context)
        chunks = self._retriever.retrieve(query, self._top_k)
        context.retrieved_chunks = chunks
        return chunks, StepLog(
            step_name=self.name,
            model=None,
            input_tokens=0,
            output_tokens=0,
            latency_ms=(time.monotonic() - start) * 1000,
            extra={"query": query, "n_chunks": len(chunks)},
        )
