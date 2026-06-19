# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path


project_root = Path.cwd().resolve()
icon_path = project_root / "docs" / "app_icon.ico"
env_path = project_root / ".env"
datas = [(str(env_path), ".")] if env_path.exists() else []
logo_path = project_root / "DESIGN" / "arai_logo.png"
if logo_path.exists():
    datas.append((str(logo_path), "DESIGN"))


a = Analysis(
    ["main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=["webview.platforms.edgechromium", "webview.platforms.winforms"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
