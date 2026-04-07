from __future__ import annotations

from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
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

from app.services.master_service import MasterService
from app.ui.widgets.busy_indicator import run_with_busy
from app.ui.widgets.message_box import ask_yes_no, show_error, show_info
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError


class StaffMasterScreen(QWidget):
    def __init__(self, master_service: MasterService) -> None:
        super().__init__()
        self._master_service = master_service
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
        title = QLabel("担当者マスタ")
        title.setObjectName("sectionTitle")
        self._search_edit = QLineEdit()
        self._search_edit.setObjectName("compactField")
        self._search_edit.setPlaceholderText("担当者ID / 担当者名")
        search_button = QPushButton("検索")
        search_button.setObjectName("compactSecondaryButton")
        search_button.clicked.connect(self._confirm_search)
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(self._search_edit)
        title_row.addWidget(search_button)

        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["担当者ID", "担当者名", "部署", "かな", "表示"])
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

        edit_title = QLabel("担当者編集")
        edit_title.setObjectName("sectionTitle")
        edit_layout.addWidget(edit_title)

        self._staff_id_edit = QLineEdit()
        self._staff_id_edit.setEnabled(False)
        self._name_edit = QLineEdit()
        self._department_combo = QComboBox()
        self._department_combo.addItems(["製造", "数値", "その他"])
        self._kana_edit = QLineEdit()
        self._staff_id_edit.setObjectName("compactField")
        self._name_edit.setObjectName("compactField")
        self._department_combo.setObjectName("compactField")
        self._kana_edit.setObjectName("compactField")
        self._visible_check = QCheckBox("表示する")
        self._visible_check.setObjectName("inlineCheck")

        for label_text, widget in [
            ("担当者ID", self._staff_id_edit),
            ("担当者名", self._name_edit),
            ("部署", self._department_combo),
            ("かな", self._kana_edit),
        ]:
            edit_layout.addLayout(self._field(label_text, widget))

        edit_layout.addWidget(self._visible_check)

        save_button = QPushButton("更新")
        save_button.setObjectName("compactPrimaryButton")
        save_button.clicked.connect(self._handle_save_clicked)
        edit_layout.addStretch()
        edit_layout.addWidget(save_button)

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
                rows = self._master_service.search_staff_master(query)
            else:
                rows = run_with_busy(
                    self,
                    title="担当者マスタ検索",
                    message="担当者マスタを検索しています...",
                    task=lambda: self._master_service.search_staff_master(query),
                )
        except (AppConfigurationError, AppDataAccessError) as exc:
            self._table.setRowCount(0)
            if not silent:
                show_error(self, "担当者マスタ", str(exc))
            return

        self._populate_table(rows)

    def _confirm_search(self) -> None:
        if not ask_yes_no(self, "担当者マスタ検索", "担当者マスタを検索しますか？"):
            return
        self._search()

    def _handle_selection_changed(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            return
        self._staff_id_edit.setText(self._table.item(row, 0).text())
        self._name_edit.setText(self._table.item(row, 1).text())
        department = self._table.item(row, 2).text()
        index = self._department_combo.findText(department)
        if index >= 0:
            self._department_combo.setCurrentIndex(index)
        self._kana_edit.setText(self._table.item(row, 3).text())
        self._visible_check.setChecked(self._table.item(row, 4).text().upper() == "Y")

    def _handle_save_clicked(self) -> None:
        if not ask_yes_no(self, "担当者マスタ更新", "担当者情報を更新しますか？"):
            return
        staff_id = self._staff_id_edit.text()
        name = self._name_edit.text()
        department = self._department_combo.currentText()
        kana = self._kana_edit.text()
        visible = self._visible_check.isChecked()
        search_query = self._search_edit.text()
        try:
            rows = run_with_busy(
                self,
                title="担当者マスタ更新",
                message="担当者情報を更新しています...",
                task=lambda: self._update_staff_and_reload(
                    staff_id=staff_id,
                    name=name,
                    department=department,
                    kana=kana,
                    visible=visible,
                    search_query=search_query,
                ),
            )
        except (AppValidationError, AppConfigurationError, AppDataAccessError) as exc:
            show_error(self, "担当者マスタ更新", str(exc))
            return
        show_info(self, "担当者マスタ更新", "更新しました。")
        self._populate_table(rows)

    def _update_staff_and_reload(
        self,
        *,
        staff_id: str,
        name: str,
        department: str,
        kana: str,
        visible: bool,
        search_query: str,
    ):
        self._master_service.update_staff_member(
            staff_id=staff_id,
            name=name,
            department=department,
            kana=kana,
            visible=visible,
        )
        return self._master_service.search_staff_master(search_query)

    def _populate_table(self, rows) -> None:
        self._table.setRowCount(len(rows))
        for row_index, record in enumerate(rows):
            self._table.setItem(row_index, 0, QTableWidgetItem(record.staff_id))
            self._table.setItem(row_index, 1, QTableWidgetItem(record.name))
            self._table.setItem(row_index, 2, QTableWidgetItem(record.department))
            self._table.setItem(row_index, 3, QTableWidgetItem(record.kana))
            self._table.setItem(row_index, 4, QTableWidgetItem("Y" if record.visible else "N"))
