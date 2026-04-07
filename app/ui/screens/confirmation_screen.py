from __future__ import annotations

from datetime import date, datetime

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.loan_record import LoanRecord
from app.services.operation_service import OperationService
from app.ui.widgets.busy_indicator import run_with_busy
from app.ui.widgets.message_box import ask_yes_no, show_error, show_info
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError


class ConfirmationScreen(QWidget):
    def __init__(self, operation_service: OperationService) -> None:
        super().__init__()
        self._operation_service = operation_service
        self._selected_loan_id: int | None = None
        self._build_ui()
        self._refresh_batches(silent=True)

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        left_card = QFrame()
        left_card.setObjectName("sectionCard")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(24, 22, 24, 24)
        left_layout.setSpacing(16)

        title = QLabel("確認")
        title.setObjectName("sectionTitle")
        left_layout.addWidget(title)

        self._case_no_edit = QLineEdit()
        self._case_no_edit.setObjectName("compactField")
        self._case_no_edit.setPlaceholderText("返却ケースNo")
        self._case_no_edit.setMaxLength(2)
        self._case_no_edit.setFixedWidth(196)

        search_button = QPushButton("確認対象検索")
        search_button.setObjectName("compactSecondaryButton")
        search_button.clicked.connect(self._confirm_search_clicked)

        confirm_one_button = QPushButton("個別確認")
        confirm_one_button.setObjectName("compactSecondaryButton")
        confirm_one_button.clicked.connect(self._handle_confirm_one_clicked)

        confirm_all_button = QPushButton("一括確認")
        confirm_all_button.setObjectName("compactPrimaryButton")
        confirm_all_button.clicked.connect(self._handle_confirm_all_clicked)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        case_no_label = QLabel("返却ケースNo")
        case_no_label.setObjectName("fieldLabel")
        case_no_label.setFixedWidth(76)
        search_row.addWidget(case_no_label)
        search_row.addWidget(self._case_no_edit)
        search_row.addWidget(search_button)
        search_row.addStretch()
        left_layout.addLayout(search_row)

        self._selected_label = QLabel("選択中: なし")
        self._selected_label.setObjectName("detailText")

        selected_row = QHBoxLayout()
        selected_row.setSpacing(10)
        selected_row.addWidget(self._selected_label)
        selected_row.addSpacing(120)
        selected_row.addWidget(confirm_one_button)
        selected_row.addWidget(confirm_all_button)
        selected_row.addStretch()
        left_layout.addLayout(selected_row)

        self._detail_table = QTableWidget(0, 6)
        self._detail_table.setHorizontalHeaderLabels(["ID", "サイズ", "担当者", "返却日", "ケースNo", "状態"])
        self._detail_table.verticalHeader().setVisible(False)
        self._detail_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._detail_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._detail_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._detail_table.setShowGrid(False)
        self._detail_table.itemSelectionChanged.connect(self._handle_selection_changed)

        left_layout.addWidget(self._detail_table, 1)

        right_card = QFrame()
        right_card.setObjectName("sectionCard")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(24, 20, 24, 20)
        right_layout.setSpacing(12)

        right_title = QLabel("確認待ち一覧")
        right_title.setObjectName("sectionTitle")

        refresh_button = QPushButton("再読込")
        refresh_button.setObjectName("compactSecondaryButton")
        refresh_button.clicked.connect(self._confirm_refresh_clicked)

        title_row = QHBoxLayout()
        title_row.addWidget(right_title)
        title_row.addStretch()
        title_row.addWidget(refresh_button)

        self._batch_table = QTableWidget(0, 2)
        self._batch_table.setHorizontalHeaderLabels(["返却機番", "返却日"])
        self._batch_table.verticalHeader().setVisible(False)
        self._batch_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._batch_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._batch_table.setShowGrid(False)
        self._batch_table.itemSelectionChanged.connect(self._handle_batch_selection_changed)

        right_layout.addLayout(title_row)
        right_layout.addWidget(self._batch_table)

        root.addWidget(left_card, 7)
        root.addWidget(right_card, 4)

    def _handle_search_clicked(self) -> None:
        case_no = self._case_no_edit.text()
        try:
            loans = run_with_busy(
                self,
                title="確認対象検索",
                message="確認対象を検索しています...",
                task=lambda: self._operation_service.search_confirmation_loans(case_no),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "確認対象検索", str(exc))
            return
        self._populate_detail(loans)

    def _confirm_search_clicked(self) -> None:
        if not ask_yes_no(self, "確認対象検索", "確認対象を検索しますか？"):
            return
        self._handle_search_clicked()

    def _handle_confirm_one_clicked(self) -> None:
        if not ask_yes_no(self, "個別確認", "選択した貸出を確認済みにしますか？"):
            return
        loan_id = self._selected_loan_id
        try:
            run_with_busy(
                self,
                title="個別確認",
                message="確認状態を更新しています...",
                task=lambda: self._operation_service.confirm_one(loan_id),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "個別確認", str(exc))
            return
        show_info(self, "個別確認", "個別確認しました。")
        self._handle_search_clicked()
        self._refresh_batches()

    def _handle_confirm_all_clicked(self) -> None:
        if not ask_yes_no(self, "一括確認", "表示中の貸出を全て確認済みにしますか？"):
            return
        loan_ids = [
            int(self._detail_table.item(row, 0).text())
            for row in range(self._detail_table.rowCount())
            if self._detail_table.item(row, 0) is not None
        ]
        try:
            count = run_with_busy(
                self,
                title="一括確認",
                message="確認状態を一括更新しています...",
                task=lambda: self._operation_service.confirm_all(loan_ids),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "一括確認", str(exc))
            return
        show_info(self, "一括確認", f"{count}件を確認済みにしました。")
        self._handle_search_clicked()
        self._refresh_batches()

    def _handle_selection_changed(self) -> None:
        row = self._detail_table.currentRow()
        if row < 0:
            self._selected_loan_id = None
            self._selected_label.setText("選択中: なし")
            return
        self._selected_loan_id = int(self._detail_table.item(row, 0).text())
        size_item = self._detail_table.item(row, 1)
        size_text = size_item.text() if size_item is not None else "-"
        self._selected_label.setText(f"選択中: ID={self._selected_loan_id} / サイズ={size_text}")

    def _refresh_batches(self, silent: bool = False) -> None:
        try:
            if silent:
                batches = self._operation_service.fetch_confirmation_batches()
            else:
                batches = run_with_busy(
                    self,
                    title="確認待ち一覧",
                    message="確認待ち一覧を再読込しています...",
                    task=self._operation_service.fetch_confirmation_batches,
                )
        except (AppConfigurationError, AppDataAccessError) as exc:
            self._batch_table.setRowCount(0)
            if not silent:
                show_error(self, "確認待ち一覧", str(exc))
            return

        self._batch_table.setRowCount(len(batches))
        for row_index, (machine_code, returned_on) in enumerate(batches):
            self._batch_table.setItem(row_index, 0, QTableWidgetItem(machine_code))
            self._batch_table.setItem(row_index, 1, QTableWidgetItem(self._format_date(returned_on)))

    def _confirm_refresh_clicked(self) -> None:
        if not ask_yes_no(self, "確認待ち一覧再読込", "確認待ち一覧を再読込しますか？"):
            return
        self._refresh_batches()

    def _handle_batch_selection_changed(self) -> None:
        row = self._batch_table.currentRow()
        if row < 0:
            return

        machine_item = self._batch_table.item(row, 0)
        if machine_item is None:
            return

        machine_code = machine_item.text().strip()
        case_no = self._extract_case_no(machine_code)
        if not case_no:
            return

        if not ask_yes_no(self, "確認待ち一覧選択", f"{machine_code} の確認対象を表示しますか？"):
            self._batch_table.blockSignals(True)
            self._batch_table.clearSelection()
            self._batch_table.blockSignals(False)
            return

        self._case_no_edit.setText(case_no)
        self._handle_search_clicked()

    def _populate_detail(self, loans: list[LoanRecord]) -> None:
        self._detail_table.setRowCount(len(loans))
        self._selected_loan_id = None
        self._selected_label.setText("選択中: なし")
        for row_index, loan in enumerate(loans):
            values = [
                str(loan.loan_id),
                loan.size,
                loan.staff_name,
                self._format_date(loan.returned_on),
                loan.case_no or "",
                loan.completion_flag or "未確認",
            ]
            for column_index, value in enumerate(values):
                self._detail_table.setItem(row_index, column_index, QTableWidgetItem(value))

    @staticmethod
    def _format_date(value: date | datetime | None) -> str:
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.strftime("%Y/%m/%d")
        return value.strftime("%Y/%m/%d")

    @staticmethod
    def _extract_case_no(machine_code: str) -> str:
        normalized = machine_code.strip()
        if "-" not in normalized:
            return ""
        return normalized.split("-", 1)[1].strip()
