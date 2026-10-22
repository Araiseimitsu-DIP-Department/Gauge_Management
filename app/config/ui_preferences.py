"""業務DBとは独立した、Windowsユーザーごとの表示設定。"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)
THEMES = ("light", "dark")


def theme_path() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return base / "PinGaugeMgmt" / "ui-theme.txt"


def load_theme(path: Path | None = None) -> str:
    target = path if path is not None else theme_path()
    try:
        theme = target.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return "light"
    except (OSError, UnicodeError):
        logger.warning("表示モードを読み込めないためライトモードを使用します。", exc_info=True)
        return "light"
    if theme not in THEMES:
        logger.warning("保存された表示モードが不正なためライトモードを使用します。")
        return "light"
    return theme


def save_theme(theme: str, path: Path | None = None) -> None:
    if theme not in THEMES:
        raise ValueError("表示モードはlightまたはdarkで指定してください。")
    target = path if path is not None else theme_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent, delete=False) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(theme)
        temporary_path.replace(target)
        logger.info("表示モードを保存しました: %s", theme)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
