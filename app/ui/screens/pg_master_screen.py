from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.pg_master import PgMasterRecord
from app.services.master_service import MasterService
from app.ui.widgets.busy_indicator import run_with_busy
from app.ui.widgets.message_box import ask_yes_no, show_error, show_info
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError


class PgMasterScreen(QWidget):
    def __init__(self, master_service: MasterService) -> None:
        super().__init__()
        self._master_service = master_service
        self._is_new = True
        self._build_ui()
        self._search(silent=True)

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        list_card = QFrame()
        list_card.setObjectName("sectionCard")
        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(24, 20, 24, 20)
        list_layout.setSpacing(12)

        title_row = QHBoxLayout()
        title = QLabel("PGマスタ")
        title.setObjectName("sectionTitle")
        self._search_edit = QLineEdit()
        self._search_edit.setObjectName("compactField")
        self._search_edit.setPlaceholderText("サイズ検索")
        search_button = QPushButton("検索")
        search_button.setObjectName("compactSecondaryButton")
        search_button.clicked.connect(self._confirm_search)

        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(self._search_edit)
        title_row.addWidget(search_button)

        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["サイズ", "保有数", "ケースNo"])
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.itemSelectionChanged.connect(self._handle_selection_changed)

        list_layout.addLayout(title_row)
        list_layout.addWidget(self._table)

        edit_card = QFrame()
        edit_card.setObjectName("sectionCard")
        edit_layout = QVBoxLayout(edit_card)
        edit_layout.setContentsMargins(24, 22, 24, 24)
        edit_layout.setSpacing(14)

        edit_title = QLabel("編集")
        edit_title.setObjectName("sectionTitle")
        edit_layout.addWidget(edit_title)

        self._size_edit = QLineEdit()
        self._holding_spin = QSpinBox()
        self._size_edit.setObjectName("compactField")
        self._holding_spin.setObjectName("compactField")
        self._holding_spin.setRange(0, 99999)
        self._case_no_edit = QLineEdit()
        self._case_no_edit.setObjectName("compactField")
        self._case_no_edit.setMaxLength(20)

        for label_text, widget in [
            ("サイズ", self._size_edit),
            ("保有数", self._holding_spin),
            ("ケースNo", self._case_no_edit),
        ]:
            edit_layout.addLayout(self._field(label_text, widget))

        button_row = QHBoxLayout()
        new_button = QPushButton("新規")
        new_button.setObjectName("compactSecondaryButton")
        new_button.clicked.connect(self._confirm_new_clicked)
        save_button = QPushButton("保存")
        save_button.setObjectName("compactPrimaryButton")
        save_button.clicked.connect(self._handle_save_clicked)
        delete_button = QPushButton("削除")
        delete_button.setObjectName("compactGhostButton")
        delete_button.clicked.connect(self._handle_delete_clicked)
        button_row.addWidget(new_button)
        button_row.addWidget(save_button)
        button_row.addWidget(delete_button)
        edit_layout.addStretch()
        edit_layout.addLayout(button_row)

        root.addWidget(list_card, 7)
        root.addWidget(edit_card, 4)

    def _field(self, label_text: str, widget: QWidget) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.setSpacing(6)
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout

    def _search(self, silent: bool = False) -> None:
        query = self._search_edit.text()
        try:
            if silent:
                rows = self._master_service.search_pg_master(query)
            else:
                rows = run_with_busy(
                    self,
                    title="PGマスタ検索",
                    message="PGマスタを検索しています...",
                    task=lambda: self._master_service.search_pg_master(query),
                )
        except (AppConfigurationError, AppDataAccessError) as exc:
            self._table.setRowCount(0)
            if not silent:
                show_error(self, "PGマスタ", str(exc))
            return

        self._populate_table(rows)

    def _confirm_search(self) -> None:
        if not ask_yes_no(self, "PGマスタ検索", "PGマスタを検索しますか？"):
            return
        self._search()

    def _handle_selection_changed(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            return
        self._is_new = False
        self._size_edit.setText(self._table.item(row, 0).text())
        self._size_edit.setEnabled(False)
        self._holding_spin.setValue(int(self._table.item(row, 1).text()))
        self._case_no_edit.setText(self._table.item(row, 2).text())

    def _handle_new_clicked(self) -> None:
        self._is_new = True
        self._size_edit.clear()
        self._size_edit.setEnabled(True)
        self._holding_spin.setValue(0)
        self._case_no_edit.clear()

    def _confirm_new_clicked(self) -> None:
        if not ask_yes_no(self, "PGマスタ新規", "入力欄を新規登録用にクリアしますか？"):
            return
        self._handle_new_clicked()

    def _handle_save_clicked(self) -> None:
        if not ask_yes_no(self, "PGマスタ保存", "入力内容を保存しますか？"):
            return
        size = self._size_edit.text()
        holding_count = self._holding_spin.value()
        case_no = self._case_no_edit.text()
        is_new = self._is_new
        search_query = self._search_edit.text()
        try:
            rows = run_with_busy(
                self,
                title="PGマスタ保存",
                message="PGマスタを保存しています...",
                task=lambda: self._save_pg_master_and_reload(
                    size=size,
                    holding_count=holding_count,
                    case_no=case_no,
                    is_new=is_new,
                    search_query=search_query,
                ),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "PGマスタ保存", str(exc))
            return
        show_info(self, "PGマスタ保存", "保存しました。")
        self._populate_table(rows)

    def _handle_delete_clicked(self) -> None:
        if not ask_yes_no(self, "PGマスタ削除", "このサイズを削除しますか？"):
            return
        size = self._size_edit.text()
        search_query = self._search_edit.text()
        try:
            rows = run_with_busy(
                self,
                title="PGマスタ削除",
                message="PGマスタを削除しています...",
                task=lambda: self._delete_pg_master_and_reload(
                    size=size,
                    search_query=search_query,
                ),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "PGマスタ削除", str(exc))
            return
        show_info(self, "PGマスタ削除", "削除しました。")
        self._handle_new_clicked()
        self._populate_table(rows)

    def _save_pg_master_and_reload(
        self,
        *,
        size: str,
        holding_count: int,
        case_no: str,
        is_new: bool,
        search_query: str,
    ) -> list[PgMasterRecord]:
        self._master_service.save_pg_master(
            size=size,
            holding_count=holding_count,
            case_no=case_no,
            is_new=is_new,
        )
        return self._master_service.search_pg_master(search_query)

    def _delete_pg_master_and_reload(self, *, size: str, search_query: str) -> list[PgMasterRecord]:
        self._master_service.delete_pg_master(size)
        return self._master_service.search_pg_master(search_query)

    def _populate_table(self, rows: list[PgMasterRecord]) -> None:
        self._table.setRowCount(len(rows))
        for row_index, record in enumerate(rows):
            self._table.setItem(row_index, 0, QTableWidgetItem(record.size))
            self._table.setItem(row_index, 1, QTableWidgetItem(str(record.holding_count)))
            self._table.setItem(row_index, 2, QTableWidgetItem(record.case_no))
