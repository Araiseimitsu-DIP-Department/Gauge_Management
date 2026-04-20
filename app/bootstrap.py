from __future__ import annotations

import webview

from app.application.usecases.lending_usecase import LendingUseCase
from app.application.usecases.master_usecase import MasterUseCase
from app.application.usecases.operation_usecase import OperationUseCase
from app.config.app_settings import load_app_settings
from app.infrastructure.repository_factory import build_repository_bundle
from app.services.lending_service import LendingService
from app.services.master_service import MasterService
from app.services.operation_service import OperationService
from app.webview.backend import WebviewBridge
from app.webview.frontend import build_html

def run() -> int:
    settings = load_app_settings()
    repositories = build_repository_bundle(settings)

    lending_service = LendingService(LendingUseCase(repositories.lending))
    operation_service = OperationService(OperationUseCase(repositories.operation))
    master_service = MasterService(MasterUseCase(repositories.master))

    bridge = WebviewBridge(
        settings=settings,
        lending_service=lending_service,
        operation_service=operation_service,
        master_service=master_service,
    )

    webview.create_window(
        settings.app_name,
        html=build_html(settings.app_name),
        js_api=bridge,
        width=1440,
        height=900,
        min_size=(1260, 780),
        maximized=True,
        background_color="#f5f7fa",
        confirm_close=True,
    )

    webview.start(
        debug=False,
        localization={
            "global.quitConfirmation": "アプリを終了しますか？",
            "global.ok": "OK",
            "global.quit": "終了",
            "global.cancel": "キャンセル",
        },
    )
    return 0
