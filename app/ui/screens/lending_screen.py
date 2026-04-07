from __future__ import annotations

from datetime import date, datetime

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
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

from app.config.app_settings import AppSettings
from app.models.loan_record import LoanRecord
from app.models.staff import StaffMember
from app.services.lending_service import LendingService
from app.ui.dialogs.loan_edit_dialog import LoanEditDialog
from app.ui.widgets.busy_indicator import run_with_busy
from app.ui.widgets.date_picker import DatePickerField
from app.ui.widgets.message_box import ask_yes_no, show_error, show_info
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError
from app.utils.validators import NUMBER_MACHINE_PREFIX


class _SequentialSizeLineEdit(QLineEdit):
    advanceRequested = Signal()

    def keyPressEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        if event.key() in {Qt.Key_Return, Qt.Key_Enter}:
            self.advanceRequested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class LendingScreen(QWidget):
    def __init__(self, settings: AppSettings, lending_service: LendingService) -> None:
        super().__init__()
        self._settings = settings
        self._lending_service = lending_service
        self._gauge_inputs: list[QLineEdit] = []
        self._staff_members: list[StaffMember] = []
        self._current_loans: list[LoanRecord] = []
        self._selected_loan: LoanRecord | None = None
        self._result_count_label: QLabel | None = None
        self._search_mode = "size"
        self._build_ui()
        self._reload_staff_members(silent=True)
        self._populate_loans([])

    def _build_ui(self) -> None:
        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(20)
        root_layout.addWidget(self._build_registration_panel(), 4)
        root_layout.addWidget(self._build_list_panel(), 5)

    def _build_registration_panel(self) -> QFrame:
        card = QFrame()
        card.setObjectName("sectionCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 22)
        layout.setSpacing(16)

        title = QLabel("貸出登録")
        title.setObjectName("sectionTitle")

        self._input_count_label = QLabel("0件")
        self._input_count_label.setObjectName("metricInlineValue")

        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title_row.addWidget(title)
        title_row.addWidget(self._input_count_label)
        title_row.addStretch()

        top_row = QGridLayout()
        top_row.setHorizontalSpacing(0)
        top_row.setVerticalSpacing(12)
        top_row.setColumnStretch(0, 1)

        self._lent_on_edit = DatePickerField()
        self._lent_on_edit.setDate(QDate.currentDate())
        self._lent_on_edit.set_compact(True)
        self._lent_on_edit.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self._lent_on_edit.setFixedWidth(196)

        machine_row = self._build_machine_input_row(
            prefix_attr="_register_machine_prefix_combo",
            suffix_attr="_register_machine_suffix_combo",
            on_prefix_change=self._handle_register_machine_prefix_changed,
            suffix_change_handler=self._update_register_machine_display,
            display_attr="_register_machine_display",
        )

        self._staff_combo = QComboBox()
        self._staff_combo.setObjectName("compactField")
        self._staff_combo.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self._staff_combo.setFixedWidth(192)

        top_row.addLayout(self._inline_field("日付", self._lent_on_edit, label_width=36), 0, 0)
        top_row.addLayout(self._inline_field("機番", machine_row, label_width=36), 1, 0)
        top_row.addLayout(self._inline_field("担当者名", self._staff_combo, label_width=52), 2, 0)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        register_button = QPushButton("登録")
        register_button.setObjectName("compactPrimaryButton")
        register_button.clicked.connect(self._handle_register_clicked)
        self._register_button = register_button

        clear_button = QPushButton("中止")
        clear_button.setObjectName("compactGhostButton")
        clear_button.clicked.connect(self._confirm_clear_clicked)

        button_row.addWidget(register_button)
        button_row.addWidget(clear_button)
        button_row.addStretch()

        size_title = QLabel("サイズ入力")
        size_title.setObjectName("fieldLabel")

        size_columns = QHBoxLayout()
        size_columns.setSpacing(22)

        left_column = QVBoxLayout()
        left_column.setSpacing(10)

        right_column = QVBoxLayout()
        right_column.setSpacing(10)

        for index in range(20):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)

            input_widget = _SequentialSizeLineEdit()
            input_widget.setObjectName("sizeInput")
            input_widget.setPlaceholderText("サイズ")
            input_widget.setFixedHeight(34)
            input_widget.advanceRequested.connect(
                lambda index=index: self._focus_next_gauge_input(index)
            )
            input_widget.textChanged.connect(self._update_input_count)
            self._gauge_inputs.append(input_widget)

            label = QLabel(str(index + 1))
            label.setObjectName("sizeIndexLabel")
            label.setFixedWidth(26)

            row_layout.addWidget(label)
            row_layout.addWidget(input_widget, 1)

            if index < 10:
                left_column.addLayout(row_layout)
            else:
                right_column.addLayout(row_layout)

        size_columns.addLayout(left_column, 1)
        size_columns.addLayout(right_column, 1)

        note = QLabel("21種類を超える場合は、いったん20件まで登録して続けて追加してください。")
        note.setObjectName("noteText")
        note.setWordWrap(True)

        layout.addLayout(title_row)
        layout.addLayout(top_row)
        layout.addLayout(button_row)
        layout.addWidget(size_title)
        layout.addLayout(size_columns)
        layout.addSpacing(6)
        layout.addWidget(note)
        layout.addStretch()
        self._update_register_machine_display()
        self._update_input_count()
        self._configure_size_input_navigation()
        return card

    def _build_list_panel(self) -> QFrame:
        card = QFrame()
        card.setObjectName("sectionCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 22)
        layout.setSpacing(14)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        title = QLabel("貸出一覧")
        title.setObjectName("sectionTitle")

        self._result_count_label = QLabel("0件")
        self._result_count_label.setObjectName("metricInlineValue")

        title_row.addWidget(title)
        title_row.addWidget(self._result_count_label)
        title_row.addSpacing(20)

        self._search_by_size_button = QPushButton("サイズ")
        self._search_by_size_button.setObjectName("filterToggleButton")
        self._search_by_size_button.setCheckable(True)
        self._search_by_size_button.clicked.connect(
            lambda: self._confirm_search_mode_change("size")
        )

        self._search_by_machine_button = QPushButton("機番")
        self._search_by_machine_button.setObjectName("filterToggleButton")
        self._search_by_machine_button.setCheckable(True)
        self._search_by_machine_button.clicked.connect(
            lambda: self._confirm_search_mode_change("machine")
        )

        self._size_prefix_checkbox = QCheckBox("から始まる")
        self._size_prefix_checkbox.setObjectName("inlineCheck")

        search_mode_label = QLabel("検索項目")
        search_mode_label.setObjectName("fieldLabel")
        title_row.addStretch(0)
        title_row.addSpacing(80)
        title_row.addWidget(search_mode_label)
        title_row.addWidget(self._search_by_size_button)
        title_row.addWidget(self._search_by_machine_button)
        title_row.addStretch(1)

        search_row = QHBoxLayout()
        search_row.setSpacing(12)

        self._search_size_edit = QLineEdit()
        self._search_size_edit.setObjectName("compactField")
        self._search_size_edit.setPlaceholderText("サイズ")
        self._search_size_edit.setFixedWidth(220)

        search_machine_row = self._build_machine_input_row(
            prefix_attr="_search_machine_prefix_combo",
            suffix_attr="_search_machine_suffix_combo",
            on_prefix_change=self._handle_search_machine_prefix_changed,
            suffix_change_handler=self._update_search_machine_display,
            display_attr="_search_machine_display",
        )

        search_buttons = QVBoxLayout()
        search_buttons.setSpacing(8)

        search_button = QPushButton("検索")
        search_button.setObjectName("compactPrimaryButton")
        search_button.clicked.connect(self._confirm_search_clicked)

        clear_button = QPushButton("一覧クリア")
        clear_button.setObjectName("compactGhostButton")
        clear_button.clicked.connect(self._confirm_list_clear_clicked)

        search_buttons.addWidget(search_button)
        search_buttons.addWidget(clear_button)
        search_buttons.addStretch()

        size_search_row = QHBoxLayout()
        size_search_row.setSpacing(10)
        size_label = QLabel("サイズ")
        size_label.setObjectName("fieldLabel")
        size_label.setFixedWidth(28)
        size_search_row.addWidget(size_label)
        size_search_row.addWidget(self._search_size_edit)
        size_search_row.addSpacing(20)
        size_search_row.addWidget(self._size_prefix_checkbox)
        size_search_row.addStretch()

        machine_search_row = QHBoxLayout()
        machine_search_row.setSpacing(10)
        machine_label = QLabel("機番")
        machine_label.setObjectName("fieldLabel")
        machine_label.setFixedWidth(28)
        machine_search_row.addWidget(machine_label)
        machine_search_row.addWidget(search_machine_row)
        machine_search_row.addStretch()

        search_wrapper = QVBoxLayout()
        search_wrapper.setSpacing(8)
        search_wrapper.addLayout(size_search_row)
        search_wrapper.addLayout(machine_search_row)

        search_row.addLayout(search_wrapper, 1)
        search_row.addLayout(search_buttons)

        self._loan_table = QTableWidget(0, 6)
        self._loan_table.setObjectName("loanTable")
        self._loan_table.setHorizontalHeaderLabels(
            ["貸出日", "機番", "サイズ", "保有", "担当者名", "状態"]
        )
        self._loan_table.verticalHeader().setVisible(False)
        self._loan_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._loan_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._loan_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._loan_table.setAlternatingRowColors(True)
        self._loan_table.horizontalHeader().setStretchLastSection(True)
        self._loan_table.setShowGrid(False)
        self._loan_table.itemSelectionChanged.connect(self._handle_selection_changed)

        footer_row = QHBoxLayout()
        footer_row.setSpacing(10)
        footer_row.addStretch()

        edit_button = QPushButton("選択行を修正")
        edit_button.setObjectName("compactSecondaryButton")
        edit_button.clicked.connect(self._confirm_edit_clicked)

        footer_row.addWidget(edit_button)

        layout.addLayout(title_row)
        layout.addLayout(search_row)
        layout.addWidget(self._loan_table, 1)
        layout.addLayout(footer_row)

        self._set_search_mode("size")
        self._handle_search_machine_prefix_changed()
        self._update_search_machine_display()
        return card

    def _build_machine_input_row(
        self,
        *,
        prefix_attr: str,
        suffix_attr: str,
        on_prefix_change,
        suffix_change_handler=None,
        display_attr: str | None = None,
    ) -> QWidget:
        container = QWidget()
        container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        prefix_combo = QComboBox()
        prefix_combo.setEditable(True)
        prefix_combo.setInsertPolicy(QComboBox.NoInsert)
        prefix_combo.addItems(["", NUMBER_MACHINE_PREFIX, "A", "B", "C", "D"])
        prefix_combo.currentTextChanged.connect(on_prefix_change)
        prefix_combo.setFixedWidth(96)
        prefix_combo.setObjectName("compactField")

        hyphen = QLabel(" - ")
        hyphen.setObjectName("inlineText")

        suffix_edit = QComboBox()
        suffix_edit.setEditable(True)
        suffix_edit.setInsertPolicy(QComboBox.NoInsert)
        suffix_edit.addItems([""] + [str(index) for index in range(1, 17)])
        suffix_edit.setFixedWidth(96)
        suffix_edit.setObjectName("compactField")
        if suffix_change_handler is not None:
            suffix_edit.currentTextChanged.connect(suffix_change_handler)

        setattr(self, prefix_attr, prefix_combo)
        setattr(self, suffix_attr, suffix_edit)

        layout.addWidget(prefix_combo)
        layout.addWidget(hyphen)
        layout.addWidget(suffix_edit, 1)
        if display_attr is not None:
            display_label = QLabel("(未入力)")
            display_label.setObjectName("compactReadoutValue")
            display_label.setFixedWidth(128)
            setattr(self, display_attr, display_label)
            layout.addWidget(display_label)
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

    def _configure_size_input_navigation(self) -> None:
        if not self._gauge_inputs:
            return

        self.setTabOrder(self._lent_on_edit, self._register_machine_prefix_combo)
        self.setTabOrder(self._register_machine_prefix_combo, self._register_machine_suffix_combo)
        self.setTabOrder(self._register_machine_suffix_combo, self._staff_combo)
        self.setTabOrder(self._staff_combo, self._gauge_inputs[0])
        for current_input, next_input in zip(self._gauge_inputs, self._gauge_inputs[1:]):
            self.setTabOrder(current_input, next_input)
        self.setTabOrder(self._gauge_inputs[-1], self._register_button)

    def _focus_next_gauge_input(self, current_index: int) -> None:
        next_index = current_index + 1
        if next_index < len(self._gauge_inputs):
            self._gauge_inputs[next_index].setFocus()
            self._gauge_inputs[next_index].selectAll()
            return

        self._register_button.setFocus()

    def _update_input_count(self) -> None:
        entered_count = sum(1 for gauge_input in self._gauge_inputs if gauge_input.text().strip())
        self._input_count_label.setText(f"{entered_count}件")

    def _handle_register_machine_prefix_changed(self) -> None:
        current_prefix = self._register_machine_prefix_combo.currentText()
        is_number_machine = current_prefix == NUMBER_MACHINE_PREFIX
        has_prefix = bool(current_prefix)
        self._register_machine_suffix_combo.setEnabled(has_prefix and not is_number_machine)
        if not has_prefix or is_number_machine:
            self._register_machine_suffix_combo.setCurrentIndex(0)
        self._update_register_machine_display()
        self._reload_staff_members(silent=False)

    def _handle_search_machine_prefix_changed(self) -> None:
        current_prefix = self._search_machine_prefix_combo.currentText()
        is_number_machine = current_prefix == NUMBER_MACHINE_PREFIX
        has_prefix = bool(current_prefix)
        self._search_machine_suffix_combo.setEnabled(
            has_prefix and not is_number_machine and self._search_mode == "machine"
        )
        if not has_prefix or is_number_machine:
            self._search_machine_suffix_combo.setCurrentIndex(0)
        self._update_search_machine_display()

    def _update_register_machine_display(self) -> None:
        prefix = self._register_machine_prefix_combo.currentText().strip()
        suffix = self._register_machine_suffix_combo.currentText().strip()

        if prefix == NUMBER_MACHINE_PREFIX:
            machine_code = NUMBER_MACHINE_PREFIX
        elif prefix and suffix:
            machine_code = f"{prefix}-{suffix}"
        else:
            machine_code = "(未入力)"

        self._register_machine_display.setText(machine_code)

    def _update_search_machine_display(self) -> None:
        prefix = self._search_machine_prefix_combo.currentText().strip()
        suffix = self._search_machine_suffix_combo.currentText().strip()

        if prefix == NUMBER_MACHINE_PREFIX:
            machine_code = NUMBER_MACHINE_PREFIX
        elif prefix and suffix:
            machine_code = f"{prefix}-{suffix}"
        else:
            machine_code = "(未入力)"

        self._search_machine_display.setText(machine_code)

    def _reload_staff_members(self, *, silent: bool) -> None:
        current_text = self._register_machine_prefix_combo.currentText()
        selected_staff_id = self._staff_combo.currentData()
        self._staff_combo.clear()

        if not current_text:
            self._staff_members = []
            self._staff_combo.addItem("", None)
            self._staff_combo.setEnabled(False)
            return

        try:
            if silent:
                self._staff_members = self._lending_service.load_staff_members(current_text)
            else:
                self._staff_members = run_with_busy(
                    self,
                    title="担当者読込",
                    message="担当者候補を読み込んでいます...",
                    task=lambda: self._lending_service.load_staff_members(current_text),
                )
        except (AppConfigurationError, AppDataAccessError) as exc:
            self._staff_members = []
            self._staff_combo.addItem("担当者を読み込めません")
            self._staff_combo.setEnabled(False)
            if not silent:
                show_error(self, "担当者読込", str(exc))
            return

        self._staff_combo.addItem("", None)
        for staff in self._staff_members:
            self._staff_combo.addItem(staff.name, staff.staff_id)
        self._staff_combo.setEnabled(True)

        if selected_staff_id is not None:
            selected_index = self._staff_combo.findData(selected_staff_id)
            if selected_index >= 0:
                self._staff_combo.setCurrentIndex(selected_index)

    def _confirm_search_mode_change(self, mode: str) -> None:
        if mode == self._search_mode:
            self._set_search_mode(mode)
            return

        mode_label = "サイズ" if mode == "size" else "機番"
        if not ask_yes_no(self, "検索項目切替", f"検索項目を{mode_label}に切り替えますか？"):
            self._set_search_mode(self._search_mode)
            return

        self._set_search_mode(mode)

    def _confirm_search_clicked(self) -> None:
        if not ask_yes_no(self, "貸出一覧検索", "貸出一覧を検索しますか？"):
            return
        self._handle_search_clicked()

    def _confirm_edit_clicked(self) -> None:
        if not ask_yes_no(self, "貸出修正", "選択した貸出の修正画面を開きますか？"):
            return
        self._handle_edit_clicked()

    def _confirm_clear_clicked(self) -> None:
        if not ask_yes_no(self, "貸出登録入力クリア", "貸出登録の入力内容をクリアしますか？"):
            return
        self._handle_clear_clicked()

    def _confirm_list_clear_clicked(self) -> None:
        if not ask_yes_no(self, "貸出一覧クリア", "貸出一覧の検索条件と表示結果をクリアしますか？"):
            return
        self._handle_list_clear_clicked()

    def _handle_search_clicked(self) -> None:
        search_mode = self._search_mode
        size_prefix = self._search_size_edit.text()
        machine_prefix = self._search_machine_prefix_combo.currentText()
        machine_suffix = self._search_machine_suffix_combo.currentText()
        use_size_prefix_match = self._size_prefix_checkbox.isChecked()
        try:
            loans = run_with_busy(
                self,
                title="貸出一覧検索",
                message="貸出一覧を検索しています...",
                task=lambda: self._lending_service.search_loans(
                    search_mode=search_mode,
                    size_prefix=size_prefix,
                    machine_prefix=machine_prefix,
                    machine_suffix=machine_suffix,
                    use_size_prefix_match=use_size_prefix_match,
                ),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "貸出一覧検索", str(exc))
            return

        self._populate_loans(loans)

    def _handle_edit_clicked(self) -> None:
        if self._selected_loan is None:
            show_error(self, "貸出修正", "修正対象の貸出を選択してください。")
            return

        dialog = LoanEditDialog(
            parent=self,
            lending_service=self._lending_service,
            loan=self._selected_loan,
            staff_members=self._staff_members,
        )
        if dialog.exec():
            self._handle_search_clicked()

    def _handle_clear_clicked(self) -> None:
        self._lent_on_edit.setDate(QDate.currentDate())
        self._register_machine_prefix_combo.setCurrentIndex(0)
        self._register_machine_suffix_combo.setCurrentIndex(0)
        self._staff_combo.setCurrentIndex(0)
        for gauge_input in self._gauge_inputs:
            gauge_input.clear()
        self._update_register_machine_display()

    def _handle_list_clear_clicked(self) -> None:
        self._search_size_edit.clear()
        self._search_machine_prefix_combo.setCurrentIndex(0)
        self._search_machine_suffix_combo.setCurrentIndex(0)
        self._size_prefix_checkbox.setChecked(False)
        self._populate_loans([])
        self._set_search_mode("size")

    def _handle_register_clicked(self) -> None:
        if not ask_yes_no(self, "貸出登録", "入力内容で貸出登録しますか？"):
            return

        lent_on = self._lent_on_edit.date().toPython()
        machine_prefix = self._register_machine_prefix_combo.currentText()
        machine_suffix = self._register_machine_suffix_combo.currentText()
        staff_id = self._staff_combo.currentData()
        gauge_sizes = [widget.text() for widget in self._gauge_inputs]
        try:
            loans = run_with_busy(
                self,
                title="貸出登録",
                message="貸出データを登録しています...",
                task=lambda: self._lending_service.register_loans(
                    lent_on=lent_on,
                    machine_prefix=machine_prefix,
                    machine_suffix=machine_suffix,
                    staff_id=staff_id,
                    gauge_sizes=gauge_sizes,
                ),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "貸出登録", str(exc))
            return

        self._populate_loans(loans)
        for gauge_input in self._gauge_inputs:
            gauge_input.clear()
        show_info(self, "貸出登録", "貸出登録しました。")

    def _populate_loans(self, loans: list[LoanRecord]) -> None:
        self._current_loans = loans
        self._selected_loan = None
        self._loan_table.setRowCount(len(loans))

        for row_index, loan in enumerate(loans):
            values = [
                self._format_date(loan.lent_on),
                loan.machine_code,
                loan.size,
                "" if loan.holding_count is None else str(loan.holding_count),
                loan.staff_name,
                "返却済み" if loan.returned_on else "貸出中",
            ]
            for column_index, value in enumerate(values):
                self._loan_table.setItem(row_index, column_index, QTableWidgetItem(value))
            self._loan_table.setRowHeight(row_index, 38)

        if self._result_count_label is not None:
            self._result_count_label.setText(f"{len(loans)}件")

    def _handle_selection_changed(self) -> None:
        row = self._loan_table.currentRow()
        if row < 0 or row >= len(self._current_loans):
            self._selected_loan = None
            return
        self._selected_loan = self._current_loans[row]

    def _set_search_mode(self, mode: str) -> None:
        self._search_mode = mode
        is_size_mode = mode == "size"

        self._search_by_size_button.setChecked(is_size_mode)
        self._search_by_machine_button.setChecked(not is_size_mode)
        self._search_size_edit.setEnabled(is_size_mode)
        self._size_prefix_checkbox.setEnabled(is_size_mode)
        self._search_machine_prefix_combo.setEnabled(not is_size_mode)
        self._search_machine_suffix_combo.setEnabled(
            not is_size_mode
            and bool(self._search_machine_prefix_combo.currentText())
            and self._search_machine_prefix_combo.currentText() != NUMBER_MACHINE_PREFIX
        )

    @staticmethod
    def _format_date(value: date | datetime | None) -> str:
        if value is None:
            return ""
        if isinstance(value, datetime):
            return value.strftime("%Y/%m/%d")
        return value.strftime("%Y/%m/%d")
