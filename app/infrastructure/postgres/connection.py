from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from app.config.db_settings import PostgresDbSettings
from app.shared.errors import ConfigurationError, DataAccessError


@contextmanager
def open_postgres_connection(settings: PostgresDbSettings) -> Iterator[object]:
    """Open a PostgreSQL connection lazily so the app can start without the driver installed."""
    connection_url = settings.connection_url
    if not connection_url:
        raise ConfigurationError("POSTGRES_CONNECTION_URL is not configured.")

    try:
        import psycopg
    except ImportError as exc:
        raise ConfigurationError("PostgreSQL backend requires psycopg. Install psycopg[binary].") from exc

    try:
        with psycopg.connect(connection_url) as connection:
            yield connection
    except Exception as exc:
        raise DataAccessError("Failed to connect to PostgreSQL.") from exc


@contextmanager
def open_postgres_cursor(connection: object) -> Iterator[object]:
    """Open a dict-like cursor for backend-agnostic row mapping."""
    try:
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise ConfigurationError("PostgreSQL backend requires psycopg. Install psycopg[binary].") from exc

    with connection.cursor(row_factory=dict_row) as cursor:  # type: ignore[union-attr]
        yield cursor
