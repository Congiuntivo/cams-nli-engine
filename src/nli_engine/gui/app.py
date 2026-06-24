"""NiceGUI front-end for the NLI engine, defaulting to the one-shot LLM workflow."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from nicegui import run as ng_run
from nicegui import ui

from nli_engine.cli.logging import configure_file_logging, initialize_trace_loggers
from nli_engine.engine.client import build_client
from nli_engine.engine.conversation import Conversation
from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.registry import WORKFLOW_REGISTRY
from nli_engine.engine.workflow.result import TurnResult
from nli_engine.gui import status as status_handler
from nli_engine.gui import theme

_SERVER_URL = "http://localhost:8080"
_WORKFLOW_ID = "one_shot_llm"
_LOG_DIR = Path("gui_logs")
_CONFIG_PATH = Path("config.yaml")
_WELCOME_MD = (
    "### Author a CARP Protocol\n\n"
    "Enter a detailed natural-language description of the study protocol you "
    "want to author, and the engine will assemble it for you."
)

theme.install_static()

_logging_initialised = False
_session_log = logging.getLogger("nli_engine.session")


def _ensure_logging() -> None:
    """Initialise trace loggers and JSONL file logging once per process."""
    global _logging_initialised
    if _logging_initialised:
        return
    initialize_trace_loggers()
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    configure_file_logging(_LOG_DIR)
    _logging_initialised = True


@ui.page("/")
def _index() -> None:
    """Render the single-page protocol authoring UI."""
    theme.apply_page()
    state: dict[str, Any] = {
        "current_status": "",
        "displayed_status": "",
        "result": None,
        "name": "",
    }

    with ui.header(elevated=True).classes(
        "items-center gap-4 px-6 py-3 bg-primary text-white"
    ):
        ui.image(theme.LOGO_URL).style(
            "width: 164px; height: 28px; object-fit: contain"
        )
        ui.label("Protocol Authoring Service").classes("text-sm opacity-80")

    with ui.column().classes("w-full max-w-3xl mx-auto my-8 gap-4 px-4"):
        with ui.card().props("flat bordered").classes("w-full p-8 rounded-lg"):
            ui.markdown(_WELCOME_MD)

            with ui.column().classes("w-full gap-3 mt-2"):
                name_input = (
                    ui.input(label="Protocol name")
                    .props("outlined dense")
                    .classes("w-1/2")
                )
                description_input = (
                    ui.textarea(
                        label="Describe the protocol you wish to author",
                        placeholder=(
                            "e.g. Collect heart rate every 5 minutes via a Polar H10 "
                            "and prompt the participant once a day at 8pm "
                            "to take a voice note describing their mood and stress level."
                        ),
                    )
                    .props("outlined autogrow input-style='min-height:160px'")
                    .classes("w-full")
                )
                with ui.row().classes("w-full justify-end mt-2"):
                    run_button = ui.button(
                        "Author protocol",
                        on_click=lambda: _start_run(),
                    ).props("unelevated rounded color=primary size=md")

        status_card = (
            ui.card().props("flat").classes("w-full p-4 rounded-lg items-center")
        )
        status_card.style(f"background-color: {theme.PRIMARY_LIGHT}")
        with status_card:
            with ui.row().classes("items-center gap-3"):
                ui.spinner(size="md", color="primary")
                status_label = (
                    ui.label("").classes("text-base").style(f"color: {theme.HEADING}")
                )
        status_card.set_visibility(False)

        result_container = ui.column().classes("w-full gap-4")
        result_container.set_visibility(False)

    async def _start_run() -> None:
        name = (name_input.value or "").strip()
        description = (description_input.value or "").strip()
        if not name:
            ui.notify("Please provide a protocol name.", type="warning")
            return
        if not description:
            ui.notify("Please provide a description.", type="warning")
            return

        state["name"] = name
        state["current_status"] = "Starting..."
        state["displayed_status"] = ""
        state["result"] = None

        run_button.disable()
        name_input.disable()
        description_input.disable()
        result_container.clear()
        result_container.set_visibility(False)
        status_label.text = "Starting..."
        status_card.set_visibility(True)

        _ensure_logging()
        _session_log.info(
            "session_start",
            extra={
                "event": "session_start",
                "workflow": _WORKFLOW_ID,
                "protocol_name": name,
            },
        )

        config = (
            WorkflowConfig.from_yaml(_CONFIG_PATH)
            if _CONFIG_PATH.exists()
            else WorkflowConfig()
        )
        session = ProtocolSession(build_client(_SERVER_URL), name=name)
        try:
            conversation = Conversation(
                WORKFLOW_REGISTRY[_WORKFLOW_ID], config, session
            )
        except KeyError as exc:
            run_button.enable()
            name_input.enable()
            description_input.enable()
            status_card.set_visibility(False)
            ui.notify(
                f"Missing model in WorkflowConfig: {exc}. "
                f"Add a 'models.default' (or per-step) entry to ./config.yaml.",
                type="negative",
                multi_line=True,
                close_button=True,
            )
            return
        handler = status_handler.attach(
            lambda label: state.__setitem__("current_status", label)
        )

        def _poll() -> None:
            current = state["current_status"]
            if current and current != state["displayed_status"]:
                state["displayed_status"] = current
                status_label.text = current

        timer = ui.timer(0.2, _poll)

        error: str | None = None
        result: TurnResult | None = None
        try:
            result = await ng_run.io_bound(conversation.turn, description)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        finally:
            status_handler.detach(handler)
            timer.deactivate()
            run_button.enable()
            name_input.enable()
            description_input.enable()
            status_card.set_visibility(False)

        if error is not None:
            ui.notify(error, type="negative", multi_line=True, close_button=True)
            return

        assert result is not None
        state["result"] = result
        _render_result(result, name)

    def _render_result(result: TurnResult, name: str) -> None:
        result_container.clear()
        with result_container:
            with ui.card().props("flat bordered").classes("w-full p-6 rounded-lg"):
                ui.label("Explanation").classes("text-lg font-bold").style(
                    f"color: {theme.HEADING}"
                )
                ui.markdown(result.message or "_(no explanation returned)_").classes(
                    "mt-2"
                )

            if result.partial_failures:
                failures_card = ui.card().props("flat").classes("w-full p-4 rounded-lg")
                failures_card.style(
                    f"background-color: {theme.WARNING_TINT}; "
                    f"border-left: 4px solid {theme.COLORS['warning']}"
                )
                with failures_card:
                    ui.label("Partial failures").classes("font-bold").style(
                        f"color: {theme.HEADING}"
                    )
                    for failure in result.partial_failures:
                        ui.label(f"• {failure}").style(f"color: {theme.TEXT}")

            if result.protocol is not None:
                with ui.card().props("flat bordered").classes("w-full p-6 rounded-lg"):
                    ui.label("Protocol JSON").classes("text-lg font-bold").style(
                        f"color: {theme.HEADING}"
                    )
                    json_str = json.dumps(result.protocol, indent=2)
                    ui.code(json_str, language="json").classes(
                        "w-full max-h-96 overflow-auto mt-2 rounded"
                    )
                    with ui.row().classes("w-full justify-end mt-3"):
                        ui.button(
                            "Download JSON",
                            on_click=lambda: ui.download.content(
                                json_str, filename=f"{name}.json"
                            ),
                            icon="download",
                        ).props("unelevated rounded color=primary")

            with ui.row().classes("w-full justify-end"):
                ui.button("Start over", on_click=_reset).props(
                    "flat rounded color=primary"
                )
        result_container.set_visibility(True)

    def _reset() -> None:
        name_input.value = ""
        description_input.value = ""
        status_label.text = ""
        result_container.clear()
        result_container.set_visibility(False)
        state["current_status"] = ""
        state["displayed_status"] = ""
        state["result"] = None
        state["name"] = ""


def run() -> None:
    """Launch the NiceGUI server on http://localhost:3000."""
    ui.run(
        host="0.0.0.0",
        port=3000,
        title="CARP Protocol Authoring Service",
        reload=False,
        show=False,
    )
