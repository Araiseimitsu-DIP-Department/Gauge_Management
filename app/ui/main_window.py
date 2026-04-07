from __future__ import annotations

from functools import partial

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.config.app_settings import AppSettings
from app.services.lending_service import LendingService
from app.services.master_service import MasterService
from app.services.operation_service import OperationService
from app.ui.screens.confirmation_screen import ConfirmationScreen
from app.ui.screens.lending_screen import LendingScreen
from app.ui.screens.pg_master_screen import PgMasterScreen
from app.ui.screens.return_screen import ReturnScreen
from app.ui.screens.staff_master_screen import StaffMasterScreen
from app.ui.styles.theme import APP_STYLESHEET


class MainWindow(QMainWindow):
    def __init__(
        self,
        settings: AppSettings,
        lending_service: LendingService,
        operation_service: OperationService,
        master_service: MasterService,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._lending_service = lending_service
        self._operation_service = operation_service
        self._master_service = master_service
        self._nav_buttons: dict[str, QPushButton] = {}
        self._master_buttons: dict[str, QPushButton] = {}
        self._screen_titles: dict[str, tuple[str, str]] = {
            "lending": ("貸出", "貸出登録と貸出一覧"),
            "return": ("返却", "返却対象の検索と返却処理"),
            "confirmation": ("確認", "返却済みデータの確認"),
            "pg_master": ("PGマスタ", "サイズ、保有数、ケースNoの管理"),
            "staff_master": ("担当者マスタ", "担当者情報の管理"),
        }
        self.setWindowTitle(settings.app_name)
        self.resize(1440, 900)
        self.setMinimumSize(1260, 780)
        self.setStyleSheet(APP_STYLESHEET)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._create_sidebar())
        root_layout.addWidget(self._create_content_area(), 1)

        self.setCentralWidget(root)
        self._switch_screen("lending")

    def _create_sidebar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("sidebar")
        frame.setFixedWidth(224)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 24, 18, 18)
        layout.setSpacing(10)

        title = QLabel("ピンゲージ管理")
        title.setObjectName("sidebarTitle")
        title.setWordWrap(True)

        layout.addWidget(title)
        layout.addSpacing(18)

        self._add_nav_button(layout, "lending", "貸出")
        self._add_nav_button(layout, "return", "返却")
        self._add_nav_button(layout, "confirmation", "確認")

        layout.addStretch()

        self._master_toggle_button = QPushButton("マスタ管理")
        self._master_toggle_button.setObjectName("navGroupButton")
        self._master_toggle_button.setCheckable(True)
        self._master_toggle_button.clicked.connect(self._toggle_master_menu)
        layout.addWidget(self._master_toggle_button)

        self._master_menu = QWidget()
        master_layout = QVBoxLayout(self._master_menu)
        master_layout.setContentsMargins(10, 4, 0, 0)
        master_layout.setSpacing(6)

        self._add_master_nav_button(master_layout, "pg_master", "PGマスタ")
        self._add_master_nav_button(master_layout, "staff_master", "担当者マスタ")
        self._master_menu.setVisible(False)

        layout.addWidget(self._master_menu)
        return frame

    def _create_content_area(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(18)

        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        self._page_title = QLabel()
        self._page_title.setObjectName("pageTitle")

        self._page_subtitle = QLabel()
        self._page_subtitle.setObjectName("pageSubtitle")

        header_row.addWidget(self._page_title)
        header_row.addWidget(self._page_subtitle)
        header_row.addStretch()

        self._stack = QStackedWidget()
        self._screens = {
            "lending": LendingScreen(self._settings, self._lending_service),
            "return": ReturnScreen(self._operation_service),
            "confirmation": ConfirmationScreen(self._operation_service),
            "pg_master": PgMasterScreen(self._master_service),
            "staff_master": StaffMasterScreen(self._master_service),
        }

        for screen in self._screens.values():
            self._stack.addWidget(screen)

        layout.addLayout(header_row)
        layout.addWidget(self._stack, 1)
        return wrapper

    def _add_nav_button(self, layout: QVBoxLayout, screen_key: str, label_text: str) -> None:
        button = QPushButton(label_text)
        button.setCheckable(True)
        button.setObjectName("navButton")
        button.clicked.connect(partial(self._switch_screen, screen_key))
        layout.addWidget(button)
        self._nav_buttons[screen_key] = button

    def _add_master_nav_button(self, layout: QVBoxLayout, screen_key: str, label_text: str) -> None:
        button = QPushButton(label_text)
        button.setCheckable(True)
        button.setObjectName("navSubButton")
        button.clicked.connect(partial(self._switch_screen, screen_key))
        layout.addWidget(button)
        self._master_buttons[screen_key] = button

    def _switch_screen(self, screen_key: str) -> None:
        for key, button in self._nav_buttons.items():
            button.setChecked(key == screen_key)
        for key, button in self._master_buttons.items():
            button.setChecked(key == screen_key)

        is_master_screen = screen_key in self._master_buttons
        self._master_toggle_button.setChecked(is_master_screen)
        self._master_menu.setVisible(is_master_screen or self._master_menu.isVisible())

        self._stack.setCurrentWidget(self._screens[screen_key])
        title, subtitle = self._screen_titles[screen_key]
        self._page_title.setText(title)
        self._page_subtitle.setText(f"〈{subtitle}〉")

    def _toggle_master_menu(self) -> None:
        should_show = self._master_toggle_button.isChecked()
        self._master_menu.setVisible(should_show)
