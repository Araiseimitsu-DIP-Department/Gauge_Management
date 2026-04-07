from __future__ import annotations

from PySide6.QtWidgets import QWidget

from app.ui.widgets.modal_dialog import show_modal


def show_info(parent: QWidget, title: str, message: str) -> None:
    show_modal(
        parent=parent,
        dialog_type="info",
        title=title,
        message=message,
        buttons=[("OK", "ok")],
        default_result="ok",
    )


def show_warning(parent: QWidget, title: str, message: str) -> None:
    show_modal(
        parent=parent,
        dialog_type="warning",
        title=title,
        message=message,
        buttons=[("OK", "ok")],
        default_result="ok",
    )


def show_error(parent: QWidget, title: str, message: str) -> None:
    show_modal(
        parent=parent,
        dialog_type="error",
        title=title,
        message=message,
        buttons=[("OK", "ok")],
        default_result="ok",
    )


def ask_yes_no(parent: QWidget, title: str, message: str) -> bool:
    result = show_modal(
        parent=parent,
        dialog_type="question",
        title=title,
        message=message,
        buttons=[("いいえ", "no"), ("はい", "yes")],
        default_result="yes",
    )
    return result == "yes"
