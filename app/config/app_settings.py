from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from app.config.db_settings import (
    DATABASE_BACKEND_KEY,
    AccessDbSettings,
    PostgresDbSettings,
    load_access_db_settings,
    load_postgres_db_settings,
)
from app.utils.env_loader import load_env_file


@dataclass(frozen=True)
class AppSettings:
    app_name: str
    environment: str
    database_backend: str
    access_db: AccessDbSettings
    postgres_db: PostgresDbSettings


def load_app_settings(env_file: Path | None = None) -> AppSettings:
    env_path = env_file or _resolve_default_env_file()
    env_values = load_env_file(env_path) if env_path is not None else {}

    return AppSettings(
        app_name=env_values.get("APP_NAME", "ピンゲージ管理").strip() or "ピンゲージ管理",
        environment=env_values.get("APP_ENV", "local").strip() or "local",
        database_backend=env_values.get(DATABASE_BACKEND_KEY, "access").strip().lower() or "access",
        access_db=load_access_db_settings(env_values),
        postgres_db=load_postgres_db_settings(env_values),
    )


def _resolve_default_env_file() -> Path | None:
    """Resolve the most appropriate .env file for local or frozen execution."""
    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / ".env")
        candidates.append(Path(sys.executable).resolve().parent / ".env")
    else:
        project_root = Path(__file__).resolve().parents[2]
        candidates.extend([project_root / ".env", project_root / ".env.example"])
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
