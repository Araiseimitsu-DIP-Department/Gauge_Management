from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import pyodbc

from app.config.db_settings import AccessDbSettings
from app.utils.errors import AppConfigurationError


def build_access_connection_string(settings: AccessDbSettings) -> str:
    """Build a DSN-less connection string for a local Access database."""
    if settings.database_path is None:
        raise AppConfigurationError("ACCESS_DB_DIRECTORY が設定されていません。")

    return (
        "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={settings.database_path};"
    )


@contextmanager
def open_access_connection(settings: AccessDbSettings) -> Iterator[pyodbc.Connection]:
    database_path = settings.database_path
    if database_path is None:
        raise AppConfigurationError("Access 保存先フォルダが未設定です。")

    try:
        database_exists = database_path.exists()
    except OSError as exc:
        raise AppConfigurationError(
            f"Access ファイルへアクセスできません: {database_path}"
        ) from exc

    if not database_exists:
        raise AppConfigurationError(
            f"Access ファイルが見つかりません: {database_path}"
        )

    connection = pyodbc.connect(build_access_connection_string(settings), autocommit=False)
    try:
        yield connection
    finally:
        connection.close()
