from __future__ import annotations

from unittest.mock import MagicMock

from nli_engine.engine.llm.client import LLMResponse
from nli_engine.engine.retrieval.chunk import RetrievedChunk
from nli_engine.engine.retrieval.retriever import Retriever
from nli_engine.engine.workflow.base import Message, WorkflowContext
from nli_engine.engine.workflow.steps.llm import LLMStep


class _ConcreteContext(WorkflowContext):
    pass


class _FixedRetriever(Retriever):
    def __init__(
        self, chunks: list[RetrievedChunk], captured: list[str] | None = None
    ) -> None:
        self._chunks = chunks
        self._captured = captured

    def retrieve(
        self, query: str, top_k: int = 5, min_score: float = 0.0
    ) -> list[RetrievedChunk]:
        if self._captured is not None:
            self._captured.append(query)
        filtered = [c for c in self._chunks if c.score >= min_score]
        return filtered[:top_k]


CHUNKS = [
    RetrievedChunk(content="alpha text", score=1.0, source="doc-a"),
    RetrievedChunk(content="beta text", score=0.75, source="doc-b"),
]


def _make_client(text: str = "ok") -> MagicMock:
    client = MagicMock()
    client.model = "test-model"
    client.complete.return_value = LLMResponse(
        text=text, tool_calls=[], input_tokens=1, output_tokens=1
    )
    return client


def _make_ctx(*user_messages: str) -> _ConcreteContext:
    return _ConcreteContext(
        history=[Message(role="user", content=m) for m in user_messages]
    )


def test_retriever_is_called_with_last_user_message() -> None:
    captured: list[str] = []
    step = LLMStep(
        name="s",
        client=_make_client(),
        system_prompt="context: {{var: retrieved_context}}",
        retriever=_FixedRetriever(CHUNKS, captured),
    )
    step.run(_make_ctx("find me something"))
    assert captured == ["find me something"]


def test_chunks_appear_in_rendered_system_prompt() -> None:
    client = _make_client()
    step = LLMStep(
        name="s",
        client=client,
        system_prompt="ctx: {{var: retrieved_context}}",
        retriever=_FixedRetriever(CHUNKS),
    )
    step.run(_make_ctx("query"))
    sent_messages = client.complete.call_args[0][0]
    system_content = sent_messages[0]["content"]
    assert "doc-a" in system_content
    assert "alpha text" in system_content
    assert "doc-b" in system_content
    assert "beta text" in system_content


def test_no_retriever_leaves_prompt_unchanged() -> None:
    client = _make_client()
    step = LLMStep(name="s", client=client, system_prompt="plain prompt")
    step.run(_make_ctx("hi"))
    sent = client.complete.call_args[0][0]
    assert sent[0]["content"] == "plain prompt"


def test_step_log_extra_contains_query_and_n_chunks() -> None:
    step = LLMStep(
        name="s",
        client=_make_client(),
        system_prompt="{{var: retrieved_context}}",
        retriever=_FixedRetriever(CHUNKS),
    )
    _, log = step.run(_make_ctx("my query"))
    assert log.extra["query"] == "my query"
    assert log.extra["n_chunks"] == len(CHUNKS)


def test_step_log_extra_is_empty_without_retriever() -> None:
    step = LLMStep(name="s", client=_make_client(), system_prompt="plain")
    _, log = step.run(_make_ctx("hi"))
    assert log.extra == {}


def test_custom_query_extractor_is_used() -> None:
    captured: list[str] = []

    class _StaticExtractor:
        def extract(self, context: WorkflowContext) -> str:
            return "custom query"

    step = LLMStep(
        name="s",
        client=_make_client(),
        system_prompt="{{var: retrieved_context}}",
        retriever=_FixedRetriever(CHUNKS, captured),
        query_extractor=_StaticExtractor(),
    )
    step.run(_make_ctx("ignored"))
    assert captured == ["custom query"]


def test_top_k_is_forwarded_to_retriever() -> None:
    many = [RetrievedChunk(content=str(i), score=1.0, source=str(i)) for i in range(10)]
    client = _make_client()
    step = LLMStep(
        name="s",
        client=client,
        system_prompt="{{var: retrieved_context}}",
        retriever=_FixedRetriever(many),
        top_k=3,
    )
    step.run(_make_ctx("q"))
    sent = client.complete.call_args[0][0][0]["content"]
    # Only 3 chunks rendered — sources 0, 1, 2 present; 3 absent
    assert 'source="0"' in sent
    assert 'source="2"' in sent
    assert 'source="3"' not in sent


def test_empty_retrieval_result_renders_empty_string() -> None:
    client = _make_client()
    step = LLMStep(
        name="s",
        client=client,
        system_prompt="ctx: {{var: retrieved_context}}",
        retriever=_FixedRetriever([]),
    )
    step.run(_make_ctx("q"))
    sent = client.complete.call_args[0][0][0]["content"]
    assert sent == "ctx: "
