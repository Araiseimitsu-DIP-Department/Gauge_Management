from __future__ import annotations

from datetime import date, datetime

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.models.loan_record import LoanRecord
from app.models.staff import StaffMember
from app.services.lending_service import LendingService
from app.ui.widgets.busy_indicator import run_with_busy
from app.ui.widgets.date_picker import DatePickerField
from app.ui.widgets.message_box import ask_yes_no, show_error, show_info
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError
from app.utils.validators import NUMBER_MACHINE_PREFIX


class LoanEditDialog(QDialog):
    def __init__(
        self,
        *,
        parent: QWidget | None,
        lending_service: LendingService,
        loan: LoanRecord,
        staff_members: list[StaffMember],
    ) -> None:
        super().__init__(parent)
        self._lending_service = lending_service
        self._loan = loan
        self._staff_members = self._resolve_staff_members(staff_members)
        self.setWindowTitle("貸出修正")
        self.setMinimumWidth(420)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self._date_edit = DatePickerField()
        lent_on = self._loan.lent_on.date() if isinstance(self._loan.lent_on, datetime) else self._loan.lent_on
        self._date_edit.setDate(QDate(lent_on.year, lent_on.month, lent_on.day) if isinstance(lent_on, date) else QDate.currentDate())
        self._date_edit.set_compact(True)

        self._machine_edit = QLineEdit(self._loan.machine_code)
        self._size_edit = QLineEdit(self._loan.size)
        self._staff_combo = QComboBox()
        self._machine_edit.setObjectName("compactField")
        self._size_edit.setObjectName("compactField")
        self._staff_combo.setObjectName("compactField")
        self._staff_combo.addItem("担当者を選択してください", None)
        for staff in self._staff_members:
            self._staff_combo.addItem(staff.name, staff.staff_id)
        current_index = self._staff_combo.findData(self._loan.staff_id)
        if current_index >= 0:
            self._staff_combo.setCurrentIndex(current_index)
        elif self._loan.staff_id:
            self._staff_combo.addItem(
                self._loan.staff_name or self._loan.staff_id,
                self._loan.staff_id,
            )
            self._staff_combo.setCurrentIndex(self._staff_combo.count() - 1)

        for label_text, widget in [
            ("貸出日", self._date_edit),
            ("機番", self._machine_edit),
            ("サイズ", self._size_edit),
            ("担当者", self._staff_combo),
        ]:
            layout.addLayout(self._field(label_text, widget))

        button_row = QHBoxLayout()
        delete_button = QPushButton("削除")
        delete_button.setObjectName("compactGhostButton")
        delete_button.clicked.connect(self._handle_delete)
        save_button = QPushButton("更新")
        save_button.setObjectName("compactPrimaryButton")
        save_button.clicked.connect(self._handle_save)
        button_row.addWidget(delete_button)
        button_row.addWidget(save_button)

        layout.addLayout(button_row)

    def _field(self, label_text: str, widget: QWidget) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(6)
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout

    def _resolve_staff_members(self, initial_staff_members: list[StaffMember]) -> list[StaffMember]:
        machine_prefix = self._extract_machine_prefix(self._loan.machine_code)
        if not machine_prefix:
            return initial_staff_members

        try:
            staff_members = run_with_busy(
                self.parentWidget(),
                title="担当者読込",
                message="担当者候補を読み込んでいます...",
                task=lambda: self._lending_service.load_staff_members(machine_prefix),
            )
        except (AppConfigurationError, AppDataAccessError):
            return initial_staff_members

        return staff_members or initial_staff_members

    @staticmethod
    def _extract_machine_prefix(machine_code: str) -> str:
        normalized = machine_code.strip()
        if not normalized:
            return ""
        if normalized == NUMBER_MACHINE_PREFIX:
            return NUMBER_MACHINE_PREFIX
        return normalized.split("-", 1)[0]

    def _handle_save(self) -> None:
        if not ask_yes_no(self, "貸出修正", "選択した貸出を更新しますか？"):
            return
        loan_id = self._loan.loan_id
        lent_on = self._date_edit.date().toPython()
        machine_code = self._machine_edit.text()
        staff_id = self._staff_combo.currentData()
        size = self._size_edit.text()
        try:
            run_with_busy(
                self,
                title="貸出修正",
                message="貸出データを更新しています...",
                task=lambda: self._lending_service.update_loan(
                    loan_id=loan_id,
                    lent_on=lent_on,
                    machine_code=machine_code,
                    staff_id=staff_id,
                    size=size,
                ),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "貸出修正", str(exc))
            return
        show_info(self, "貸出修正", "更新しました。")
        self.accept()

    def _handle_delete(self) -> None:
        if not ask_yes_no(self, "貸出削除", "選択した貸出を削除しますか？"):
            return
        loan_id = self._loan.loan_id
        try:
            run_with_busy(
                self,
                title="貸出削除",
                message="貸出データを削除しています...",
                task=lambda: self._lending_service.delete_loan(loan_id),
            )
        except (AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "貸出削除", str(exc))
            return
        show_info(self, "貸出削除", "削除しました。")
        self.accept()
