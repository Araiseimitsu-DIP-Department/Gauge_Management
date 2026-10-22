from __future__ import annotations

import base64
import sys
from pathlib import Path

from app.config.ui_preferences import load_theme
from app.version import APP_VERSION
from app.webview.frontend_styles import STYLES
from app.webview.frontend_layout import LAYOUT_STYLES
from app.webview.frontend_theme import THEME_SCRIPT, THEME_STYLES
from app.webview.frontend_render import SCRIPT as RENDER_SCRIPT
from app.webview.frontend_controller import SCRIPT as CONTROLLER_SCRIPT
from app.webview.frontend_events import SCRIPT as EVENTS_SCRIPT
from app.webview.frontend_dates import SCRIPT as DATES_SCRIPT


def build_html(app_name: str) -> str:
    return (
        _HTML.replace("__APP_STYLES__", STYLES + THEME_STYLES + LAYOUT_STYLES)
        .replace("__THEME_SCRIPT__", THEME_SCRIPT)
        .replace("__APP_SCRIPT__", RENDER_SCRIPT + CONTROLLER_SCRIPT + DATES_SCRIPT + EVENTS_SCRIPT)
        .replace("__INITIAL_THEME__", load_theme())
        .replace("__APP_VERSION__", APP_VERSION)
        .replace("__APP_NAME__", _escape_html(app_name))
        .replace("__ARAI_LOGO__", _load_arai_logo_data_uri())
    )


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _load_arai_logo_data_uri() -> str:
    for logo_path in _iter_logo_candidates():
        try:
            encoded = base64.b64encode(logo_path.read_bytes()).decode("ascii")
        except OSError:
            continue
        return f"data:image/png;base64,{encoded}"
    return ""


def _iter_logo_candidates() -> list[Path]:
    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            base = Path(meipass)
            candidates.extend(
                [
                    base / "DESIGN" / "arai_logo.png",
                    base / "arai_logo.png",
                ]
            )
        candidates.append(Path(sys.executable).resolve().parent / "DESIGN" / "arai_logo.png")
    project_root = Path(__file__).resolve().parents[2]
    candidates.extend(
        [
            project_root / "DESIGN" / "arai_logo.png",
            Path.cwd() / "DESIGN" / "arai_logo.png",
        ]
    )

    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


_HTML = r"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>__APP_NAME__</title>
  <style>
__APP_STYLES__
  </style>
  <script>__THEME_SCRIPT__</script>
</head>
<body>
  <div id="app"></div>
  <div id="modal-root"></div>
  <div id="dialog-root"></div>
  <div id="busy-root"></div>
  <script>
__APP_SCRIPT__
  </script>
</body>
</html>
"""
