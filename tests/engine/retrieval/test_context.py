from nli_engine.engine.retrieval.chunk import RetrievedChunk
from nli_engine.engine.retrieval.context import RetrievalContext


class _ConcreteRetrievalContext(RetrievalContext):
    pass


def test_retrieved_chunks_defaults_to_empty() -> None:
    ctx = _ConcreteRetrievalContext()
    assert ctx.retrieved_chunks == []


def test_context_variables_returns_empty_string_when_no_chunks() -> None:
    ctx = _ConcreteRetrievalContext()
    variables = ctx.context_variables()
    assert variables == {"retrieved_context": ""}


def test_context_variables_formats_single_chunk() -> None:
    ctx = _ConcreteRetrievalContext(
        retrieved_chunks=[
            RetrievedChunk(content="some text", score=0.8, source="doc-1")
        ]
    )
    variables = ctx.context_variables()
    assert "doc-1" in variables["retrieved_context"]
    assert "0.80" in variables["retrieved_context"]
    assert "some text" in variables["retrieved_context"]


def test_context_variables_formats_multiple_chunks_separated() -> None:
    ctx = _ConcreteRetrievalContext(
        retrieved_chunks=[
            RetrievedChunk(content="first", score=1.0, source="a"),
            RetrievedChunk(content="second", score=0.5, source="b"),
        ]
    )
    rendered = ctx.context_variables()["retrieved_context"]
    assert "first" in rendered
    assert "second" in rendered
    assert rendered.index("first") < rendered.index("second")
