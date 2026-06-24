"""Carp-portal-inspired theme for the NiceGUI front-end.

Translates the Material UI palette and typography defined in
``carp-portal/src/utils/theme.tsx`` into Quasar brand colors plus a small
``<head>`` CSS block. Idempotent: ``apply()`` may be called multiple times
but only configures the runtime on the first call.
"""

from __future__ import annotations

from pathlib import Path

from nicegui import app, ui

COLORS: dict[str, str] = {
    "primary": "#006398",
    "secondary": "#5E7F97",
    "accent": "#D61D41",
    "positive": "#00A300",
    "negative": "#BA1A1A",
    "warning": "#EE9926",
    "info": "#CDE5FF",
}

PRIMARY_DARK = "#003352"
PRIMARY_LIGHT = "#CDE5FF"
BACKGROUND = "#FCFCFF"
TEXT = "#233240"
HEADING = "#001D32"
WARNING_TINT = "#FFF3D6"

_ASSETS_DIR = Path(__file__).parent / "assets"
_ASSETS_MOUNT = "/assets"

LOGO_URL = f"{_ASSETS_MOUNT}/logo-carp-flat-white.png"

HEAD_HTML = f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
  html, body, .nicegui-content,
  button, input, textarea, select,
  .q-btn, .q-field, .q-field__label, .q-field__native, .q-field__input,
  .q-card, .q-card__section, .q-toolbar, .q-toolbar__title, .q-header,
  .q-item, .q-item__label, .q-menu, .q-list, .q-tab, .q-tooltip,
  .q-notification, .q-dialog {{
    font-family: 'Open Sans', system-ui, sans-serif;
  }}
  code, pre, kbd, samp, .nicegui-code, .hljs {{
    font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  }}
  body, .nicegui-content {{
    background-color: {BACKGROUND};
    color: {TEXT};
  }}
  h1, h2, h3, h4 {{ color: {HEADING}; font-weight: 700; }}
  .q-btn {{ text-transform: none; letter-spacing: 0; }}
  .q-field--outlined .q-field__control {{ border-radius: 8px; }}
</style>
"""

_static_installed = False


def install_static() -> None:
    """Register the static asset mount once at app startup."""
    global _static_installed
    if _static_installed:
        return
    app.add_static_files(_ASSETS_MOUNT, str(_ASSETS_DIR))
    _static_installed = True


def apply_page() -> None:
    """Apply colors and head HTML for the current page.

    NiceGUI 3.x forbids UI calls at module scope when ``@ui.page`` is in use,
    so this must be invoked from inside each page handler.
    """
    ui.colors(**COLORS)
    ui.add_head_html(HEAD_HTML)
