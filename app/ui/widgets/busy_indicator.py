from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QThread, QTimer, Qt, Signal, Slot
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class _SpinnerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.start(70)
        self.setFixedSize(44, 44)

    def _rotate(self) -> None:
        self._angle = (self._angle + 24) % 360
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(6, 6, -6, -6)

        base_pen = QPen(QColor("#dce5f2"), 4)
        base_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(base_pen)
        painter.drawArc(rect, 0, 360 * 16)

        active_pen = QPen(QColor("#0d5ab6"), 4)
        active_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(active_pen)
        painter.drawArc(rect, -self._angle * 16, -110 * 16)


class _TaskWorker(QObject):
    finished = Signal(object, object)

    def __init__(self, task: Callable[[], object]) -> None:
        super().__init__(None)
        self._task = task

    @Slot()
    def run(self) -> None:
        try:
            result = self._task()
        except BaseException as exc:
            self.finished.emit(None, exc)
            return
        self.finished.emit(result, None)


class BusyDialog(QDialog):
    def __init__(self, *, parent: QWidget | None, title: str, message: str) -> None:
        super().__init__(parent)
        self._result: object | None = None
        self._error: BaseException | None = None

        self.setObjectName("modalDialog")
        self.setModal(True)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

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

        badge = QLabel("PROCESS")
        badge.setObjectName("modalBadge")
        badge.setStyleSheet("background-color: #dfe8ff; color: #365cc9;")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedHeight(32)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("modalTitle")

        message_label = QLabel(message)
        message_label.setObjectName("modalMessage")
        message_label.setWordWrap(False)

        text_layout.addWidget(title_label)
        text_layout.addWidget(message_label)

        header_row.addWidget(badge)
        header_row.addLayout(text_layout, 1)

        spinner_row = QHBoxLayout()
        spinner_row.setContentsMargins(0, 0, 0, 0)
        spinner_row.addStretch()
        spinner_row.addWidget(_SpinnerWidget(card))
        spinner_row.addStretch()

        card_layout.addLayout(header_row)
        card_layout.addLayout(spinner_row)

        outer_layout.addWidget(card)

        content_width = (
            badge.sizeHint().width()
            + header_row.spacing()
            + max(title_label.sizeHint().width(), message_label.sizeHint().width())
            + card_layout.contentsMargins().left()
            + card_layout.contentsMargins().right()
        )
        card_width = max(420, min(560, content_width + 24))
        card.setFixedWidth(card_width)

    @property
    def result_value(self) -> object | None:
        return self._result

    @property
    def error(self) -> BaseException | None:
        return self._error

    @Slot(object, object)
    def handle_finished(self, result: object, error: object) -> None:
        self._result = result
        self._error = error if isinstance(error, BaseException) else None
        self.done(0)

    def reject(self) -> None:
        return


def run_with_busy(
    parent: QWidget | None,
    *,
    title: str,
    message: str,
    task: Callable[[], object],
):
    app = QApplication.instance()
    if app is None:
        return task()

    dialog = BusyDialog(parent=parent, title=title, message=message)
    thread = QThread()
    worker = _TaskWorker(task)
    worker.moveToThread(thread)

    thread.started.connect(worker.run)
    worker.finished.connect(dialog.handle_finished, Qt.QueuedConnection)
    worker.finished.connect(thread.quit, Qt.QueuedConnection)
    thread.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    QTimer.singleShot(0, thread.start)
    dialog.exec()

    if thread.isRunning():
        thread.quit()
    thread.wait()

    if dialog.error is not None:
        raise dialog.error

    return dialog.result_value
