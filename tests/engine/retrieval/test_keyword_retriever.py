import pytest

from nli_engine.engine.retrieval.backends.keyword import KeywordRetriever
from nli_engine.engine.retrieval.document import Document

CORPUS: list[Document] = [
    Document(source="doc-a", content="The quick brown fox jumps over the lazy dog"),
    Document(source="doc-b", content="A fox ran through the forest"),
    Document(source="doc-c", content="Machine learning models require large datasets"),
    Document(source="doc-d", content="The lazy cat slept all day"),
]


def test_empty_query_returns_empty_list() -> None:
    retriever = KeywordRetriever(CORPUS)
    assert retriever.retrieve("") == []


def test_blank_query_returns_empty_list() -> None:
    retriever = KeywordRetriever(CORPUS)
    assert retriever.retrieve("   ") == []


def test_matching_chunks_are_returned() -> None:
    retriever = KeywordRetriever(CORPUS)
    results = retriever.retrieve("fox")
    sources = {c.source for c in results}
    assert "doc-a" in sources
    assert "doc-b" in sources


def test_non_matching_chunks_are_excluded() -> None:
    retriever = KeywordRetriever(CORPUS)
    results = retriever.retrieve("fox")
    sources = {c.source for c in results}
    assert "doc-c" not in sources


def test_results_are_sorted_by_descending_score() -> None:
    retriever = KeywordRetriever(CORPUS)
    results = retriever.retrieve("fox lazy")
    assert len(results) >= 2
    scores = [c.score for c in results]
    assert scores == sorted(scores, reverse=True)


def test_top_k_limits_results() -> None:
    retriever = KeywordRetriever(CORPUS)
    results = retriever.retrieve("the", top_k=2)
    assert len(results) <= 2


def test_score_is_fraction_of_matched_tokens() -> None:
    retriever = KeywordRetriever([Document(source="doc", content="fox")])
    results = retriever.retrieve("fox cat")
    assert len(results) == 1
    assert results[0].score == pytest.approx(0.5)


def test_empty_corpus_returns_empty_list() -> None:
    retriever = KeywordRetriever([])
    assert retriever.retrieve("fox") == []


def test_source_is_propagated() -> None:
    retriever = KeywordRetriever(
        [Document(source="my-source", content="unique content here")]
    )
    results = retriever.retrieve("unique")
    assert results[0].source == "my-source"
