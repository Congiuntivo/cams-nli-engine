import pytest

from nli_engine.engine.retrieval.chunk import RetrievedChunk
from nli_engine.engine.retrieval.context import RetrievalContext
from nli_engine.engine.retrieval.retriever import Retriever
from nli_engine.engine.workflow.base import Message, WorkflowContext
from nli_engine.engine.workflow.steps.retrieval import RetrievalStep


class _ConcreteRetrievalContext(RetrievalContext):
    pass


class _PlainContext(WorkflowContext):
    pass


class _FixedRetriever(Retriever):
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self._chunks = chunks

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        return self._chunks[:top_k]


CHUNKS = [
    RetrievedChunk(content="alpha", score=1.0, source="s1"),
    RetrievedChunk(content="beta", score=0.5, source="s2"),
]


def test_writes_chunks_to_context() -> None:
    step = RetrievalStep(name="ret", retriever=_FixedRetriever(CHUNKS))
    ctx = _ConcreteRetrievalContext(
        history=[Message(role="user", content="some query")]
    )
    chunks, _ = step.run(ctx)
    assert ctx.retrieved_chunks == CHUNKS


def test_returns_chunks_as_output() -> None:
    step = RetrievalStep(name="ret", retriever=_FixedRetriever(CHUNKS))
    ctx = _ConcreteRetrievalContext(history=[Message(role="user", content="query")])
    chunks, _ = step.run(ctx)
    assert chunks == CHUNKS


def test_step_log_contains_query_and_n_chunks() -> None:
    step = RetrievalStep(name="ret", retriever=_FixedRetriever(CHUNKS))
    ctx = _ConcreteRetrievalContext(history=[Message(role="user", content="my query")])
    _, log = step.run(ctx)
    assert log.extra["query"] == "my query"
    assert log.extra["n_chunks"] == len(CHUNKS)


def test_step_log_model_is_none() -> None:
    step = RetrievalStep(name="ret", retriever=_FixedRetriever(CHUNKS))
    ctx = _ConcreteRetrievalContext(history=[Message(role="user", content="q")])
    _, log = step.run(ctx)
    assert log.model is None


def test_raises_type_error_on_wrong_context() -> None:
    step = RetrievalStep(name="ret", retriever=_FixedRetriever(CHUNKS))
    ctx = _PlainContext(history=[Message(role="user", content="q")])
    with pytest.raises(TypeError, match="RetrievalContext"):
        step.run(ctx)


def test_top_k_is_forwarded_to_retriever() -> None:
    many_chunks = [
        RetrievedChunk(content=str(i), score=1.0, source=str(i)) for i in range(10)
    ]
    step = RetrievalStep(name="ret", retriever=_FixedRetriever(many_chunks), top_k=3)
    ctx = _ConcreteRetrievalContext(history=[Message(role="user", content="q")])
    chunks, _ = step.run(ctx)
    assert len(chunks) == 3


def test_default_query_extractor_uses_last_user_message() -> None:
    captured: list[str] = []

    class _CapturingRetriever(Retriever):
        def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
            captured.append(query)
            return []

    step = RetrievalStep(name="ret", retriever=_CapturingRetriever())
    ctx = _ConcreteRetrievalContext(
        history=[
            Message(role="user", content="first"),
            Message(role="assistant", content="reply"),
            Message(role="user", content="second"),
        ]
    )
    step.run(ctx)
    assert captured == ["second"]
