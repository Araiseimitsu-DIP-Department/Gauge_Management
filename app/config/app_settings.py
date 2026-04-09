from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from app.config.db_settings import AccessDbSettings, load_access_db_settings
from app.utils.env_loader import load_env_file


@dataclass(frozen=True)
class AppSettings:
    app_name: str
    environment: str
    access_db: AccessDbSettings


def load_app_settings(env_file: Path | None = None) -> AppSettings:
    env_path = env_file or _resolve_default_env_file()
    env_values = load_env_file(env_path) if env_path is not None else {}

    return AppSettings(
        app_name="ピンゲージ管理",
        environment=env_values.get("APP_ENV", "local"),
        access_db=load_access_db_settings(env_values),
    )


def _resolve_default_env_file() -> Path | None:
    """開発時はリポジトリルート。exe(onefile) 時は同梱 .env（_MEIPASS）→ exe 横 → カレントの順。"""
    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / ".env")
        candidates.append(Path(sys.executable).resolve().parent / ".env")
    else:
        project_root = Path(__file__).resolve().parents[2]
        candidates.extend(
            [
                project_root / ".env",
                project_root / ".env.example",
            ]
        )
    candidates.append(Path.cwd() / ".env")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass) / ".env"
        return Path(sys.executable).resolve().parent / ".env"
    return Path(__file__).resolve().parents[2] / ".env"
