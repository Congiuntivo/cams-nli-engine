import inspect
from unittest.mock import MagicMock, patch

import pytest

from nli_engine.client._generated.authoring_client import (
    AddExpectedParticipantDataForRoleRequest,
    AddParticipantRoleRequest,
    ApiClient,
    ExpectedParticipantDataApi,
    ImmediateTriggerRequest,
    ParticipantRolesApi,
    TriggersApi,
)
from nli_engine.engine.client import build_client
from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.tools import TOOL_REGISTRY, BoundTool

SESSION_ID = "sess-test-42"


@pytest.fixture
def session() -> ProtocolSession:
    fake_resp = MagicMock()
    fake_resp.session_id = SESSION_ID
    with patch("nli_engine.engine.session.SessionsApi") as mock_sessions:
        mock_sessions.return_value.create_protocol_session.return_value = fake_resp
        return ProtocolSession(MagicMock(), name="test")


# ------------------------------------------------------------------ #
# build_client
# ------------------------------------------------------------------ #


def test_build_client_returns_api_client():
    assert isinstance(build_client("http://localhost:8080"), ApiClient)


# ------------------------------------------------------------------ #
# TOOL_REGISTRY
# ------------------------------------------------------------------ #


def test_registry_length():
    assert len(TOOL_REGISTRY) == 44


def test_registry_entries_are_well_formed():
    for spec in TOOL_REGISTRY:
        assert spec.name, f"empty name in {spec}"
        assert spec.api_class, f"missing api_class in {spec.name}"
        assert spec.method, f"missing method in {spec.name}"
        assert spec.description, f"missing description in {spec.name}"


# ------------------------------------------------------------------ #
# ProtocolSession construction
# ------------------------------------------------------------------ #


def test_session_stores_session_id(session):
    assert session.session_id == SESSION_ID


# ------------------------------------------------------------------ #
# tools()
# ------------------------------------------------------------------ #


def test_tools_count_matches_registry(session):
    assert len(session.tools()) == len(TOOL_REGISTRY)


def test_tools_returns_bound_tools(session):
    assert all(isinstance(t, BoundTool) for t in session.tools())


def test_tools_names_match_registry(session):
    names = {t.name for t in session.tools()}
    assert names == {spec.name for spec in TOOL_REGISTRY}


# ------------------------------------------------------------------ #
# BoundTool.call — request-kwarg path
# ------------------------------------------------------------------ #


def test_call_passes_session_id_and_request_kwarg(session):
    mock_triggers = MagicMock()
    session._apis[TriggersApi] = mock_triggers

    tools = {t.name: t for t in session.tools()}
    req = ImmediateTriggerRequest(trigger_name="start")
    tools["add_immediate_trigger"].call(req)

    mock_triggers.add_immediate_trigger.assert_called_once_with(
        session_id=SESSION_ID,
        immediate_trigger_request=req,
    )


# ------------------------------------------------------------------ #
# BoundTool.call — read-only path
# ------------------------------------------------------------------ #


def test_read_only_tool_calls_with_no_args(session):
    mock_triggers = MagicMock()
    session._apis[TriggersApi] = mock_triggers

    tools = {t.name: t for t in session.tools()}
    tools["get_triggers"].call()

    mock_triggers.get_triggers.assert_called_once_with(session_id=SESSION_ID)


def test_call_passes_participant_role_request_kwarg(session):
    mock_participants = MagicMock()
    session._apis[ParticipantRolesApi] = mock_participants

    tools = {t.name: t for t in session.tools()}
    req = AddParticipantRoleRequest(role_name="participant", is_optional=False)
    tools["add_participant_role"].call(req)

    mock_participants.add_participant_role.assert_called_once_with(
        session_id=SESSION_ID,
        add_participant_role_request=req,
    )


def test_call_passes_route_and_body_for_role_scoped_request(session):
    mock_expected_data = MagicMock()
    session._apis[ExpectedParticipantDataApi] = mock_expected_data

    tools = {t.name: t for t in session.tools()}
    req = AddExpectedParticipantDataForRoleRequest(
        role_name="participant",
        data_type="sex",
    )
    tools["add_expected_data_for_role"].call(req)

    mock_expected_data.add_expected_participant_data_for_role.assert_called_once_with(
        session_id=SESSION_ID,
        add_expected_participant_data_for_role_request=req,
    )


def test_mutation_tools_bind_supported_non_session_shapes():
    for spec in TOOL_REGISTRY:
        if spec.request_model is None:
            continue

        non_session = [
            name
            for name, param in inspect.signature(
                getattr(spec.api_class, spec.method)
            ).parameters.items()
            if name not in ("self", "session_id")
            and not name.startswith("_")
            and param.kind
            not in (
                inspect.Parameter.VAR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            )
        ]
        assert len(non_session) == 1, (
            f"{spec.api_class.__name__}.{spec.method} exposes {len(non_session)} "
            f"non-session params: {non_session}"
        )
