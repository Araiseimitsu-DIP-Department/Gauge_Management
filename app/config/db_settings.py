from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


ACCESS_DB_FILENAME = "ピンゲージ管理.accdb"
ACCESS_DB_DIRECTORY_KEY = "ACCESS_DB_DIRECTORY"
DATABASE_BACKEND_KEY = "DB_BACKEND"
POSTGRES_CONNECTION_URL_KEY = "POSTGRES_CONNECTION_URL"
POSTGRES_SCHEMA_KEY = "POSTGRES_SCHEMA"


@dataclass(frozen=True)
class AccessDbSettings:
    database_directory: Path | None
    database_filename: str = ACCESS_DB_FILENAME

    @property
    def database_path(self) -> Path | None:
        if self.database_directory is None:
            return None
        return self.database_directory / self.database_filename

    @property
    def is_configured(self) -> bool:
        return self.database_directory is not None

    @property
    def exists(self) -> bool:
        database_path = self.database_path
        if database_path is None:
            return False
        try:
            return database_path.exists()
        except OSError:
            return False


@dataclass(frozen=True)
class PostgresDbSettings:
    connection_url: str | None
    schema: str = "public"

    @property
    def is_configured(self) -> bool:
        return bool(self.connection_url)


def load_access_db_settings(env_values: Mapping[str, str]) -> AccessDbSettings:
    directory_value = env_values.get(ACCESS_DB_DIRECTORY_KEY, "").strip()
    if not directory_value:
        return AccessDbSettings(database_directory=None)

    configured_path = Path(directory_value)
    if configured_path.suffix.lower() in {".accdb", ".mdb"}:
        database_directory = configured_path.parent
    else:
        database_directory = configured_path

    return AccessDbSettings(database_directory=database_directory)


def load_postgres_db_settings(env_values: Mapping[str, str]) -> PostgresDbSettings:
    connection_url = env_values.get(POSTGRES_CONNECTION_URL_KEY, "").strip() or None
    schema = env_values.get(POSTGRES_SCHEMA_KEY, "public").strip() or "public"
    return PostgresDbSettings(connection_url=connection_url, schema=schema)
