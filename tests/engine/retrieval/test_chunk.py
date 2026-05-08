import pytest

from nli_engine.engine.retrieval.chunk import RetrievedChunk


def test_fields_are_accessible() -> None:
    chunk = RetrievedChunk(content="hello", score=0.9, source="doc-1")
    assert chunk.content == "hello"
    assert chunk.score == 0.9
    assert chunk.source == "doc-1"


def test_chunk_is_frozen() -> None:
    chunk = RetrievedChunk(content="hello", score=0.9, source="doc-1")
    with pytest.raises(Exception):
        chunk.content = "modified"  # type: ignore[misc]


def test_equality_by_value() -> None:
    a = RetrievedChunk(content="x", score=1.0, source="s")
    b = RetrievedChunk(content="x", score=1.0, source="s")
    assert a == b


def test_inequality_when_fields_differ() -> None:
    a = RetrievedChunk(content="x", score=1.0, source="s")
    b = RetrievedChunk(content="y", score=1.0, source="s")
    assert a != b
