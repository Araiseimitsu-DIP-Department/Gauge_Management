# -*- mode: python ; coding: utf-8 -*-
import logging
import os
from pathlib import Path
import sys

project_root = Path(SPECPATH).resolve()
sys.path.insert(0, str(project_root))
from app.utils.env_loader import load_env_file

icon_path = project_root / "docs" / "app_icon.ico"
env_path = project_root / ".env"
build_backend = os.environ.get("PINGAUGE_BUILD_BACKEND", "postgres").strip().lower()
if build_backend not in {"postgres", "access"}:
    logging.error("PINGAUGE_BUILD_BACKENDはpostgresまたはaccessを指定してください。")
    raise ValueError("ビルド種別が不正です。")
env_values = load_env_file(env_path)
configured_backend = env_values.get("DB_BACKEND", build_backend).strip().lower() or build_backend
if configured_backend != build_backend:
    logging.error("ビルド種別と.envのDB_BACKENDが一致しません。")
    raise ValueError(".envのDB_BACKENDとPINGAUGE_BUILD_BACKENDを合わせてください。")
config_keys = ["APP_ENV", "APP_NAME"]
if build_backend == "postgres":
    config_keys += ["POSTGRES_CONNECTION_URL", "DATABASE_URL", "POSTGRES_SCHEMA"]
else:
    config_keys += ["ACCESS_DB_DIRECTORY"]
build_env_path = project_root / "build" / "config" / build_backend / ".env"
build_env_path.parent.mkdir(parents=True, exist_ok=True)
build_env_path.write_text(
    f"DB_BACKEND={build_backend}\n"
    + "".join(f"{key}={env_values[key]}\n" for key in config_keys if key in env_values),
    encoding="utf-8",
)
datas = [(str(build_env_path), ".")]
access_modules = [
    "pyodbc", "pypyodbc", "app.infrastructure.access",
    "app.repositories.access_connection", "app.repositories.lending_repository",
    "app.repositories.master_repository", "app.repositories.operation_repository",
]
logo_path = project_root / "DESIGN" / "arai_logo.png"
if logo_path.exists():
    datas.append((str(logo_path), "DESIGN"))


a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=["webview.platforms.edgechromium", "webview.platforms.winforms"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=access_modules if build_backend == "postgres" else [],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ピンゲージ管理",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path),
)
