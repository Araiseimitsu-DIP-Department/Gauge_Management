from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.application.usecases.lending_usecase import LendingUseCase
from app.application.usecases.master_usecase import MasterUseCase
from app.application.usecases.operation_usecase import OperationUseCase
from app.config.app_settings import load_app_settings
from app.infrastructure.repository_factory import build_repository_bundle
from app.services.lending_service import LendingService
from app.services.master_service import MasterService
from app.services.operation_service import OperationService
from app.ui.styles.theme import build_light_palette
from app.ui.main_window import MainWindow

# アプリアイコン画像（docs 配下。PyInstaller の --icon / datas と揃える）
_APP_ICON_FILENAME = "精密計測具のアイコン.png"


def run() -> int:
    """Application entry point."""
    settings = load_app_settings()
    repositories = build_repository_bundle(settings)

    lending_service = LendingService(LendingUseCase(repositories.lending))
    operation_service = OperationService(OperationUseCase(repositories.operation))
    master_service = MasterService(MasterUseCase(repositories.master))

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
    candidate = _app_asset_root() / "docs" / _APP_ICON_FILENAME
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
