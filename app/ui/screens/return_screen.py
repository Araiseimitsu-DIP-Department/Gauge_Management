from __future__ import annotations

from datetime import date, datetime

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.loan_record import LoanRecord
from app.services.operation_service import OperationService
from app.ui.widgets.busy_indicator import run_with_busy
from app.ui.widgets.date_picker import DatePickerField
from app.ui.widgets.message_box import ask_yes_no, show_error, show_info
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError
from app.utils.validators import NUMBER_MACHINE_PREFIX


class ReturnScreen(QWidget):
    def __init__(self, operation_service: OperationService) -> None:
        super().__init__()
        self._operation_service = operation_service
        self._selected_loan_id: int | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        left_card = QFrame()
        left_card.setObjectName("sectionCard")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(24, 22, 24, 24)
        left_layout.setSpacing(16)

        title = QLabel("返却")
        title.setObjectName("sectionTitle")

        self._date_edit = DatePickerField()
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.set_compact(True)
        self._date_edit.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self._date_edit.setFixedWidth(196)

        machine_row = self._build_machine_input_row()

        self._case_no_edit = QLineEdit()
        self._case_no_edit.setObjectName("compactField")
        self._case_no_edit.setPlaceholderText("返却ケースNo")
        self._case_no_edit.setMaxLength(2)

        self._selected_label = QLabel("選択中: なし")
        self._selected_label.setObjectName("detailText")

        left_layout.addWidget(title)
        self._case_no_edit.setFixedWidth(196)
        self._case_no_edit.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        left_layout.addLayout(self._inline_field("返却日", self._date_edit, label_width=48))
        left_layout.addLayout(self._inline_field("機番", machine_row, label_width=36))
        left_layout.addLayout(self._inline_field("返却ケースNo", self._case_no_edit, label_width=76))

        button_row = QHBoxLayout()
        button_row.setSpacing(10)

        search_button = QPushButton("返却対象検索")
        search_button.setObjectName("compactSecondaryButton")
        search_button.clicked.connect(self._confirm_search_clicked)

        clear_button = QPushButton("中止")
        clear_button.setObjectName("compactGhostButton")
        clear_button.clicked.connect(self._confirm_clear_clicked)

        button_row.addStretch()
        button_row.addWidget(search_button)
        button_row.addWidget(clear_button)
        button_row.addStretch()

        left_layout.addLayout(button_row)
        left_layout.addStretch()

        right_card = QFrame()
        right_card.setObjectName("sectionCard")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(24, 20, 24, 20)
        right_layout.setSpacing(12)

        right_title = QLabel("返却対象一覧")
        right_title.setObjectName("sectionTitle")

        right_note = QLabel("機番に紐づく未返却データを表示します。")
        right_note.setObjectName("mutedText")

        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(["ID", "サイズ", "担当者", "機番", "貸出日", "ケースNo"])
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.itemSelectionChanged.connect(self._handle_selection_changed)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        action_row.addWidget(right_note)
        action_row.addSpacing(36)

        return_one_button = QPushButton("個別返却")
        return_one_button.setObjectName("compactSecondaryButton")
        return_one_button.clicked.connect(self._handle_return_one_clicked)

        return_all_button = QPushButton("一括返却")
        return_all_button.setObjectName("compactPrimaryButton")
        return_all_button.clicked.connect(self._handle_return_all_clicked)

        action_row.addWidget(return_one_button)
        action_row.addWidget(return_all_button)

        selected_row = QHBoxLayout()
        selected_row.setSpacing(0)
        selected_row.addSpacing(420)
        selected_row.addWidget(self._selected_label)
        selected_row.addStretch()

        right_layout.addWidget(right_title)
        right_layout.addLayout(action_row)
        right_layout.addLayout(selected_row)
        right_layout.addWidget(self._table, 1)

        root.addWidget(left_card, 4)
        root.addWidget(right_card, 7)

        self._handle_machine_prefix_changed()
        self._update_machine_display()

    def _build_machine_input_row(self) -> QWidget:
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._machine_prefix_combo = QComboBox()
        self._machine_prefix_combo.setObjectName("compactField")
        self._machine_prefix_combo.setEditable(True)
        self._machine_prefix_combo.setInsertPolicy(QComboBox.NoInsert)
        self._machine_prefix_combo.addItems(["", NUMBER_MACHINE_PREFIX, "A", "B", "C", "D"])
        self._machine_prefix_combo.currentTextChanged.connect(self._handle_machine_prefix_changed)
        self._machine_prefix_combo.currentTextChanged.connect(self._update_machine_display)
        self._machine_prefix_combo.setFixedWidth(96)

        hyphen = QLabel(" - ")
        hyphen.setObjectName("inlineText")

        self._machine_suffix_combo = QComboBox()
        self._machine_suffix_combo.setObjectName("compactField")
        self._machine_suffix_combo.setEditable(True)
        self._machine_suffix_combo.setInsertPolicy(QComboBox.NoInsert)
        self._machine_suffix_combo.addItems([""] + [str(index) for index in range(1, 17)])
        self._machine_suffix_combo.setFixedWidth(96)
        self._machine_suffix_combo.currentTextChanged.connect(self._update_machine_display)

        self._machine_display = QLabel("(未入力)")
        self._machine_display.setObjectName("compactReadoutValue")
        self._machine_display.setFixedWidth(128)

        layout.addWidget(self._machine_prefix_combo)
        layout.addWidget(hyphen)
        layout.addWidget(self._machine_suffix_combo)
        layout.addWidget(self._machine_display)
        layout.addStretch()
        return container

    def _field(self, label_text: str, widget: QWidget) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(6)
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout

    def _inline_field(self, label_text: str, widget: QWidget, *, label_width: int) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(10)

        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        label.setFixedWidth(label_width)

        layout.addWidget(label)
        layout.addWidget(widget)
        layout.addStretch()
        return layout

    def _handle_machine_prefix_changed(self) -> None:
        current_prefix = self._machine_prefix_combo.currentText()
        is_number = current_prefix == NUMBER_MACHINE_PREFIX
        has_prefix = bool(current_prefix)
        self._machine_suffix_combo.setEnabled(has_prefix and not is_number)
        if not has_prefix or is_number:
            self._machine_suffix_combo.setCurrentIndex(0)

    def _update_machine_display(self) -> None:
        prefix = self._machine_prefix_combo.currentText().strip()
        suffix = self._machine_suffix_combo.currentText().strip()

        if prefix == NUMBER_MACHINE_PREFIX:
            machine_code = NUMBER_MACHINE_PREFIX
        elif prefix and suffix:
            machine_code = f"{prefix}-{suffix}"
        else:
            machine_code = "(未入力)"

        self._machine_display.setText(machine_code)

    def _handle_search_clicked(self) -> None:
        machine_prefix = self._machine_prefix_combo.currentText()
        machine_suffix = self._machine_suffix_combo.currentText()
        try:
            loans = run_with_busy(
                self,
                title="返却対象検索",
                message="返却対象を検索しています...",
                task=lambda: self._operation_service.search_returnable_loans(
                    machine_prefix,
                    machine_suffix,
                ),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "返却対象検索", str(exc))
            return

        self._populate(loans)

    def _confirm_search_clicked(self) -> None:
        if not ask_yes_no(self, "返却対象検索", "返却対象を検索しますか？"):
            return
        self._handle_search_clicked()

    def _handle_clear_clicked(self) -> None:
        self._date_edit.setDate(QDate.currentDate())
        self._machine_prefix_combo.setCurrentIndex(0)
        self._machine_suffix_combo.setCurrentIndex(0)
        self._case_no_edit.clear()
        self._selected_loan_id = None
        self._selected_label.setText("選択中: なし")
        self._table.setRowCount(0)
        self._update_machine_display()

    def _confirm_clear_clicked(self) -> None:
        if not ask_yes_no(self, "返却条件クリア", "返却条件と表示一覧をクリアしますか？"):
            return
        self._handle_clear_clicked()

    def _handle_return_one_clicked(self) -> None:
        if not ask_yes_no(self, "個別返却", "選択した貸出を返却しますか？"):
            return
        loan_id = self._selected_loan_id
        case_no = self._case_no_edit.text()
        returned_on = self._date_edit.date().toPython()
        try:
            run_with_busy(
                self,
                title="個別返却",
                message="返却データを更新しています...",
                task=lambda: self._operation_service.return_one_loan(
                    loan_id=loan_id,
                    case_no=case_no,
                    returned_on=returned_on,
                ),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "個別返却", str(exc))
            return

        show_info(self, "個別返却", "返却処理しました。")
        self._handle_search_clicked()

    def _handle_return_all_clicked(self) -> None:
        if not ask_yes_no(self, "一括返却", "表示中の貸出を全て返却しますか？"):
            return
        machine_prefix = self._machine_prefix_combo.currentText()
        machine_suffix = self._machine_suffix_combo.currentText()
        case_no = self._case_no_edit.text()
        returned_on = self._date_edit.date().toPython()
        target_count = self._table.rowCount()
        try:
            count = run_with_busy(
                self,
                title="一括返却",
                message="返却データを一括更新しています...",
                task=lambda: self._operation_service.return_all_loans(
                    machine_prefix=machine_prefix,
                    machine_suffix=machine_suffix,
                    case_no=case_no,
                    returned_on=returned_on,
                    target_count=target_count,
                ),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "一括返却", str(exc))
            return

        show_info(self, "一括返却", f"{count}件の返却処理を行いました。")
        self._handle_search_clicked()

    def _handle_selection_changed(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            self._selected_loan_id = None
            self._selected_label.setText("選択中: なし")
            return

        loan_id_item = self._table.item(row, 0)
        size_item = self._table.item(row, 1)
        self._selected_loan_id = int(loan_id_item.text()) if loan_id_item else None
        size_text = size_item.text() if size_item else "-"
        self._selected_label.setText(f"選択中: ID={self._selected_loan_id} / サイズ={size_text}")

    def _populate(self, loans: list[LoanRecord]) -> None:
        self._table.setRowCount(len(loans))
        self._selected_loan_id = None
        self._selected_label.setText("選択中: なし")

        for row_index, loan in enumerate(loans):
            values = [
                str(loan.loan_id),
                loan.size,
                loan.staff_name,
                loan.machine_code,
                self._format_date(loan.lent_on),
                loan.case_no or "",
            ]
            for column_index, value in enumerate(values):
                self._table.setItem(row_index, column_index, QTableWidgetItem(value))

    @staticmethod
    def _format_date(value: date | datetime | None) -> str:
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.strftime("%Y/%m/%d")
        return value.strftime("%Y/%m/%d")
