from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class DialogTone:
    badge_background: str
    badge_foreground: str
    eyebrow_text: str


_DIALOG_TONES = {
    "info": DialogTone("#d9ecff", "#0d5ab6", "INFO"),
    "warning": DialogTone("#fff0cf", "#a66400", "NOTICE"),
    "error": DialogTone("#ffe0dc", "#c33c14", "ERROR"),
    "question": DialogTone("#dfe8ff", "#365cc9", "CONFIRM"),
}


class ModalDialog(QDialog):
    def __init__(
        self,
        *,
        parent: QWidget | None,
        dialog_type: str,
        title: str,
        message: str,
        buttons: list[tuple[str, str]],
        default_result: str | None = None,
    ) -> None:
        super().__init__(parent)
        self._dialog_type = dialog_type
        self._title = title
        self._message = message
        self._buttons = buttons
        self._default_result = default_result
        self._result_key = default_result

        self.setObjectName("modalDialog")
        self.setModal(True)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._build_ui()

    @property
    def result_key(self) -> str | None:
        return self._result_key

    def _build_ui(self) -> None:
        tone = _DIALOG_TONES[self._dialog_type]

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(22, 22, 22, 22)

        card = QFrame()
        card.setObjectName("modalCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(18)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(42)
        shadow.setOffset(0, 16)
        shadow.setColor(QColor(12, 31, 53, 56))
        card.setGraphicsEffect(shadow)

        header_row = QHBoxLayout()
        header_row.setSpacing(14)

        badge = QLabel(tone.eyebrow_text)
        badge.setObjectName("modalBadge")
        badge.setStyleSheet(
            f"background-color: {tone.badge_background}; color: {tone.badge_foreground};"
        )
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(32)

        header_text = QVBoxLayout()
        header_text.setSpacing(4)

        title_label = QLabel(self._title)
        title_label.setObjectName("modalTitle")

        message_label = QLabel(self._message)
        message_label.setObjectName("modalMessage")
        message_label.setWordWrap(False)

        header_text.addWidget(title_label)
        header_text.addWidget(message_label)

        header_row.addWidget(badge)
        header_row.addLayout(header_text, 1)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        button_row.addStretch()
        button_widgets: list[QPushButton] = []

        for label, result_key in self._buttons:
            button = QPushButton(label)
            button.setProperty("dialogRole", result_key)
            button.setObjectName(
                "dialogPrimaryButton"
                if result_key == self._default_result
                else "dialogSecondaryButton"
            )
            button.clicked.connect(lambda checked=False, key=result_key: self._finish(key))
            button_row.addWidget(button)
            button_widgets.append(button)

        card_layout.addLayout(header_row)
        card_layout.addLayout(button_row)

        outer_layout.addWidget(card)

        content_width = (
            badge.sizeHint().width()
            + header_row.spacing()
            + max(title_label.sizeHint().width(), message_label.sizeHint().width())
            + card_layout.contentsMargins().left()
            + card_layout.contentsMargins().right()
        )
        buttons_width = (
            sum(button.sizeHint().width() for button in button_widgets)
            + max(0, len(button_widgets) - 1) * button_row.spacing()
            + card_layout.contentsMargins().left()
            + card_layout.contentsMargins().right()
            + 40
        )
        card_width = max(440, min(620, max(content_width, buttons_width)))
        card.setFixedWidth(card_width)

    def _finish(self, result_key: str) -> None:
        self._result_key = result_key
        if result_key in {"yes", "ok"}:
            self.accept()
            return
        self.reject()


def show_modal(
    *,
    parent: QWidget | None,
    dialog_type: str,
    title: str,
    message: str,
    buttons: list[tuple[str, str]],
    default_result: str | None = None,
) -> str | None:
    dialog = ModalDialog(
        parent=parent,
        dialog_type=dialog_type,
        title=title,
        message=message,
        buttons=buttons,
        default_result=default_result,
    )
    dialog.exec()
    return dialog.result_key
