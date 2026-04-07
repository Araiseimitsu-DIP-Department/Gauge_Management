from __future__ import annotations

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCalendarWidget,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class _ClickableLineEdit(QLineEdit):
    clicked = Signal()

    def mousePressEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        super().mousePressEvent(event)
        self.clicked.emit()


class CalendarDialog(QDialog):
    def __init__(self, *, parent: QWidget | None, selected_date: QDate) -> None:
        super().__init__(parent)
        self._selected_date = selected_date
        self.setObjectName("calendarDialog")
        self.setModal(True)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumSize(430, 470)
        self._build_ui()

    def selected_date(self) -> QDate:
        return self._selected_date

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(18, 18, 18, 18)

        card = QFrame()
        card.setObjectName("calendarDialogCard")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 14)
        shadow.setColor(QColor(12, 31, 53, 48))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        header_row = QHBoxLayout()
        header_row.setSpacing(8)

        prev_button = QPushButton("Prev")
        prev_button.setObjectName("calendarNavButton")
        prev_button.clicked.connect(self._show_previous_month)

        next_button = QPushButton("Next")
        next_button.setObjectName("calendarNavButton")
        next_button.clicked.connect(self._show_next_month)

        self._month_label = QLabel()
        self._month_label.setObjectName("calendarMonthLabel")
        self._month_label.setAlignment(Qt.AlignCenter)

        header_row.addWidget(prev_button)
        header_row.addStretch()
        header_row.addWidget(self._month_label)
        header_row.addStretch()
        header_row.addWidget(next_button)

        quick_row = QHBoxLayout()
        quick_row.setSpacing(8)

        today_button = QPushButton("今日")
        today_button.setObjectName("calendarPillButton")
        today_button.clicked.connect(self._jump_to_today)

        close_button = QPushButton("閉じる")
        close_button.setObjectName("calendarPillButton")
        close_button.clicked.connect(self.reject)

        quick_row.addWidget(today_button)
        quick_row.addStretch()
        quick_row.addWidget(close_button)

        self._calendar = QCalendarWidget()
        self._calendar.setObjectName("calendarWidget")
        self._calendar.setMinimumSize(360, 300)
        self._calendar.setGridVisible(False)
        self._calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self._calendar.setNavigationBarVisible(False)
        self._calendar.setSelectedDate(self._selected_date)
        self._calendar.setCurrentPage(self._selected_date.year(), self._selected_date.month())
        self._calendar.clicked.connect(self._handle_date_clicked)
        self._calendar.currentPageChanged.connect(self._update_month_label)

        footer_row = QHBoxLayout()
        footer_row.setSpacing(10)
        footer_row.addStretch()

        cancel_button = QPushButton("キャンセル")
        cancel_button.setObjectName("dialogSecondaryButton")
        cancel_button.clicked.connect(self.reject)

        decide_button = QPushButton("この日を選択")
        decide_button.setObjectName("dialogPrimaryButton")
        decide_button.clicked.connect(self._accept_selected_date)

        footer_row.addWidget(cancel_button)
        footer_row.addWidget(decide_button)

        layout.addLayout(header_row)
        layout.addLayout(quick_row)
        layout.addWidget(self._calendar)
        layout.addLayout(footer_row)

        outer_layout.addWidget(card)
        self._update_month_label(
            self._selected_date.year(),
            self._selected_date.month(),
        )

    def _show_previous_month(self) -> None:
        shown = self._calendar.monthShown()
        year = self._calendar.yearShown()
        if shown == 1:
            year -= 1
            shown = 12
        else:
            shown -= 1
        self._calendar.setCurrentPage(year, shown)

    def _show_next_month(self) -> None:
        shown = self._calendar.monthShown()
        year = self._calendar.yearShown()
        if shown == 12:
            year += 1
            shown = 1
        else:
            shown += 1
        self._calendar.setCurrentPage(year, shown)

    def _jump_to_today(self) -> None:
        today = QDate.currentDate()
        self._calendar.setSelectedDate(today)
        self._calendar.setCurrentPage(today.year(), today.month())

    def _handle_date_clicked(self, selected_date: QDate) -> None:
        self._selected_date = selected_date

    def _accept_selected_date(self) -> None:
        self._selected_date = self._calendar.selectedDate()
        self.accept()

    def _update_month_label(self, year: int, month: int) -> None:
        self._month_label.setText(f"{year:04d}.{month:02d}")


class DatePickerField(QWidget):
    dateChanged = Signal(QDate)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._date = QDate.currentDate()
        self.setMinimumHeight(46)
        self._container: QFrame | None = None
        self._build_ui()
        self._update_display()

    def date(self) -> QDate:
        return self._date

    def setDate(self, date_value: QDate) -> None:
        if not date_value.isValid():
            return
        self._date = date_value
        self._update_display()
        self.dateChanged.emit(self._date)

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self._display.setEnabled(enabled)
        self._button.setEnabled(enabled)

    def set_compact(self, compact: bool) -> None:
        compact_value = "true" if compact else "false"
        self.setProperty("compact", compact_value)
        self.setMinimumHeight(34 if compact else 46)
        if self._container is not None:
            self._container.setProperty("compact", compact_value)
            self._container.style().unpolish(self._container)
            self._container.style().polish(self._container)
        self._display.setProperty("compact", compact_value)
        self._display.style().unpolish(self._display)
        self._display.style().polish(self._display)
        self._button.setProperty("compact", compact_value)
        self._button.style().unpolish(self._button)
        self._button.style().polish(self._button)

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        container = QFrame()
        container.setObjectName("dateFieldContainer")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._container = container

        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self._display = _ClickableLineEdit()
        self._display.setObjectName("dateFieldDisplay")
        self._display.setReadOnly(True)
        self._display.setCursorPosition(0)
        self._display.setCursor(Qt.PointingHandCursor)
        self._display.clicked.connect(self._open_picker)
        self.setFocusProxy(self._display)

        self._button = QPushButton("")
        self._button.setObjectName("dateFieldButton")
        self._button.setCursor(Qt.PointingHandCursor)
        self._button.setFixedWidth(0)
        self._button.setVisible(False)
        self._button.clicked.connect(self._open_picker)

        container_layout.addWidget(self._display, 1)

        layout.addWidget(container)

    def _open_picker(self) -> None:
        if not self.isEnabled():
            return
        dialog = CalendarDialog(parent=self, selected_date=self._date)
        if dialog.exec():
            self.setDate(dialog.selected_date())

    def _update_display(self) -> None:
        self._display.setText(self._date.toString("yyyy/MM/dd"))
