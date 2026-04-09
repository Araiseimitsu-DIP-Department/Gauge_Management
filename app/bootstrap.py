from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.config.app_settings import load_app_settings
from app.repositories.lending_repository import LendingRepository
from app.repositories.master_repository import MasterRepository
from app.repositories.operation_repository import OperationRepository
from app.services.lending_service import LendingService
from app.services.master_service import MasterService
from app.services.operation_service import OperationService
from app.ui.styles.theme import build_light_palette
from app.ui.main_window import MainWindow


def run() -> int:
    """Application entry point."""
    settings = load_app_settings()
    lending_service = LendingService(LendingRepository(settings.access_db))
    operation_service = OperationService(OperationRepository(settings.access_db))
    master_service = MasterService(MasterRepository(settings.access_db))

    app = QApplication(sys.argv)
    app.setApplicationName(settings.app_name)
    app.setStyle("Fusion")
    app.setPalette(build_light_palette())
    icon = _resolve_app_icon(app)
    if icon is not None:
        app.setWindowIcon(icon)

    window = MainWindow(
        settings=settings,
        lending_service=lending_service,
        operation_service=operation_service,
        master_service=master_service,
    )
    if icon is not None:
        window.setWindowIcon(icon)
    window.showMaximized()
    return app.exec()


def _app_asset_root() -> Path:
    """開発時はプロジェクトルート、PyInstaller onefile 実行時は展開先 (_MEIPASS)。"""
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _resolve_app_icon(app: QApplication) -> QIcon | None:
    # 配布用アイコン（docs/icon.png）
    candidate = _app_asset_root() / "docs" / "icon.png"
    if candidate.exists():
        icon = QIcon(str(candidate))
        if not icon.isNull():
            return icon

    # バンドル PNG が無い場合のみ exe 埋め込みアイコンを使う（PyInstaller --icon 未設定時は効果が薄い）
    if getattr(sys, "frozen", False):
        executable_icon = QIcon(app.applicationFilePath())
        if not executable_icon.isNull():
            return executable_icon

    return None
