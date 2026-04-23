import inspect
import json
from typing import Any

from nli_engine.client._generated.authoring_client import (
    ApiClient,
    CreateProtocolRequest,
    RequirementsAndSerializationApi,
    SessionsApi,
)
from nli_engine.engine.tools import TOOL_REGISTRY, BoundTool, ToolSpec


class ProtocolSession:
    """Owns one authoring session. Exposes all mutation operations as bound tools.

    session_id is created on construction and never surfaced to the LLM.
    """

    def __init__(self, client: ApiClient, name: str, **create_kwargs: Any) -> None:
        self._client = client
        self._apis: dict[type, Any] = {}
        resp = SessionsApi(client).create_protocol_session(
            CreateProtocolRequest(name=name, **create_kwargs)
        )
        self.session_id: str = resp.session_id

    def tools(self) -> list[BoundTool]:
        """Return all LLM-callable tools with session_id pre-bound."""
        return [self._bind(spec) for spec in TOOL_REGISTRY]

    def _bind(self, spec: ToolSpec) -> BoundTool:
        api = self._apis.setdefault(spec.api_class, spec.api_class(self._client))
        method = getattr(api, spec.method)
        sid = self.session_id

        if spec.request_model is None:
            # Read-only: session_id fully pre-bound, zero remaining args.
            def call(_m: Any = method, _sid: str = sid) -> Any:
                return _m(session_id=_sid)

        else:
            # Introspect the class (not the bound instance) so the real signature
            # is always available, even when the instance is a mock in tests.
            non_session = [
                name
                for name, param in inspect.signature(
                    getattr(spec.api_class, spec.method)
                ).parameters.items()
                if name not in ("self", "session_id")
                and not name.startswith("_")
                and param.kind
                not in (inspect.Parameter.VAR_KEYWORD, inspect.Parameter.VAR_POSITIONAL)
            ]
            if len(non_session) == 1:
                # Single named request-object parameter.
                req_kwarg = non_session[0]

                def call(
                    req: Any, _m: Any = method, _sid: str = sid, _kw: str = req_kwarg
                ) -> Any:  # type: ignore[misc]
                    return _m(session_id=_sid, **{_kw: req})

            else:
                # Multiple flat parameters; unpack the local model.
                def call(req: Any, _m: Any = method, _sid: str = sid) -> Any:  # type: ignore[misc]
                    return _m(session_id=_sid, **req.model_dump(exclude_none=True))

        return BoundTool(
            name=spec.name,
            description=spec.description,
            request_model=spec.request_model,
            call=call,
        )

    # ------------------------------------------------------------------ #
    # Inspection — used by planner/conversation loop, not LLM tools
    # ------------------------------------------------------------------ #

    def get_requirements(self) -> list[str]:
        """Return currently unfulfilled requirement strings."""
        api = self._apis.setdefault(
            RequirementsAndSerializationApi,
            RequirementsAndSerializationApi(self._client),
        )
        resp = api.get_requirements(session_id=self.session_id)
        return resp.requirements or []

    def serialize(self) -> dict:
        """Return the assembled protocol as a plain dict."""
        api = self._apis.setdefault(
            RequirementsAndSerializationApi,
            RequirementsAndSerializationApi(self._client),
        )
        raw = api.serialize_protocol_without_preload_content(session_id=self.session_id)
        body = json.loads(raw.data)
        return body.get("protocol", body)
