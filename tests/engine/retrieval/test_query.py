from nli_engine.engine.retrieval.query import LastUserMessageExtractor
from nli_engine.engine.workflow.base import Message, WorkflowContext


class _ConcreteContext(WorkflowContext):
    pass


def _ctx(*messages: tuple[str, str]) -> _ConcreteContext:
    return _ConcreteContext(
        history=[Message(role=role, content=content) for role, content in messages]
    )


def test_returns_empty_string_on_empty_history() -> None:
    extractor = LastUserMessageExtractor()
    assert extractor.extract(_ctx()) == ""


def test_returns_last_user_message() -> None:
    extractor = LastUserMessageExtractor()
    ctx = _ctx(("user", "first"), ("assistant", "reply"), ("user", "second"))
    assert extractor.extract(ctx) == "second"


def test_ignores_non_user_messages() -> None:
    extractor = LastUserMessageExtractor()
    ctx = _ctx(("user", "hello"), ("assistant", "world"))
    assert extractor.extract(ctx) == "hello"


def test_returns_empty_string_when_only_assistant_messages() -> None:
    extractor = LastUserMessageExtractor()
    ctx = _ctx(("assistant", "hi"))
    assert extractor.extract(ctx) == ""


def test_returns_empty_string_when_user_message_content_is_none() -> None:
    extractor = LastUserMessageExtractor()
    ctx = _ConcreteContext(history=[Message(role="user", content=None)])
    assert extractor.extract(ctx) == ""
