from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


ACCESS_DB_FILENAME = "ピンゲージ管理.accdb"
ACCESS_DB_DIRECTORY_KEY = "ACCESS_DB_DIRECTORY"


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
