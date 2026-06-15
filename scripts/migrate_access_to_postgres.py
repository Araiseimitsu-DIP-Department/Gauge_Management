from __future__ import annotations

import argparse
import importlib
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pyodbc

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.app_settings import load_app_settings  # noqa: E402


NUMERIC_SIZE_PATTERN = re.compile(r"^[0-9]+(\.[0-9]+)?$")

TABLES = (
    ("t_PGマスタ", "pin_gauge_master"),
    ("t_担当者マスタ", "staff_master"),
    ("t_貸出", "pin_gauge_lending"),
)

SOURCE_COLUMNS = {
    "t_PGマスタ": ("サイズ", "保有数", "ケースNo"),
    "t_担当者マスタ": ("担当者ID", "担当者名", "部署", "かな", "表示"),
    "t_貸出": ("ID", "サイズ", "担当者ID", "機番", "貸出日", "返却日", "完了フラグ"),
}

TARGET_COLUMNS = {
    "pin_gauge_master": ("size", "owned_quantity", "case_no"),
    "staff_master": ("staff_id", "staff_name", "department", "kana", "display_flag"),
    "pin_gauge_lending": ("id", "size", "staff_id", "machine_no", "lent_date", "returned_date", "completion_flag"),
}


@dataclass(frozen=True)
class MigrationConfig:
    access_path: Path
    postgres_url: str
    schema: str
    apply_schema: bool
    truncate: bool
    dry_run: bool


def main() -> int:
    args = _parse_args()
    settings = load_app_settings(PROJECT_ROOT / ".env")

    access_path = Path(args.access_path) if args.access_path else settings.access_db.database_path
    postgres_url = args.postgres_url or settings.postgres_db.connection_url
    schema = args.schema or settings.postgres_db.schema or "public"

    if access_path is None:
        print("ACCESS_DB_DIRECTORY or --access-path is required.", file=sys.stderr)
        return 2
    if not postgres_url and not args.dry_run:
        print("POSTGRES_CONNECTION_URL or --postgres-url is required.", file=sys.stderr)
        return 2

    config = MigrationConfig(
        access_path=access_path,
        postgres_url=postgres_url or "",
        schema=schema,
        apply_schema=args.apply_schema,
        truncate=args.truncate,
        dry_run=args.dry_run,
    )

    try:
        migrate(config)
    except Exception as exc:
        print(f"Migration failed: {exc}", file=sys.stderr)
        return 1
    return 0


def migrate(config: MigrationConfig) -> None:
    if not config.access_path.exists():
        raise FileNotFoundError(f"Access database not found: {config.access_path}")

    psycopg = load_psycopg()

    print(f"Access: {config.access_path}")
    print(f"PostgreSQL schema: {config.schema}")

    access_connection_string = (
        "DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={config.access_path};"
    )

    with pyodbc.connect(access_connection_string, autocommit=False) as access_connection:
        extracted = {
            target_table: fetch_access_rows(access_connection, source_table, SOURCE_COLUMNS[source_table])
            for source_table, target_table in TABLES
        }

    for table_name, rows in extracted.items():
        print(f"{table_name}: {len(rows)} rows")

    reconcile_extracted_data(extracted)

    if config.dry_run:
        print("Dry run complete. PostgreSQL was not modified.")
        return

    with psycopg.connect(config.postgres_url) as postgres_connection:
        with postgres_connection.cursor() as cursor:
            cursor.execute("SET TIME ZONE 'Asia/Tokyo'")
            schema_identifier = quote_identifier(config.schema)
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_identifier}")
            cursor.execute(f"SET search_path TO {schema_identifier}")

            if config.apply_schema:
                execute_sql_file(cursor, PROJECT_ROOT / "database" / "postgresql" / "001_schema.sql")

            if config.truncate:
                cursor.execute('TRUNCATE TABLE "pin_gauge_lending", "pin_gauge_master", "staff_master" RESTART IDENTITY')

            for _, target_table in TABLES:
                insert_rows(cursor, target_table, TARGET_COLUMNS[target_table], extracted[target_table])

            reset_loan_id_sequence(cursor)

        postgres_connection.commit()

    print("Migration complete.")


def fetch_access_rows(
    connection: pyodbc.Connection,
    table_name: str,
    columns: Sequence[str],
) -> list[tuple[Any, ...]]:
    column_list = ", ".join(f"[{column}]" for column in columns)
    sql = f"SELECT {column_list} FROM [{table_name}]"
    cursor = connection.cursor()
    return [tuple(normalize_value(value) for value in row) for row in cursor.execute(sql).fetchall()]


def insert_rows(
    cursor: Any,
    table_name: str,
    columns: Sequence[str],
    rows: Sequence[tuple[Any, ...]],
) -> None:
    if not rows:
        return

    column_list = ", ".join(f'"{column}"' for column in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f'INSERT INTO "{table_name}" ({column_list}) VALUES ({placeholders})'
    cursor.executemany(sql, rows)


def reconcile_extracted_data(extracted: dict[str, list[tuple[Any, ...]]]) -> None:
    pg_master_rows = extracted["pin_gauge_master"]
    loan_rows = extracted["pin_gauge_lending"]

    master_sizes = {str(row[0]) for row in pg_master_rows if row[0] is not None}
    normalized_loans: list[tuple[Any, ...]] = []

    for row in loan_rows:
        size = row[1]
        normalized_size = normalize_loan_size(size, master_sizes)
        normalized_row = (row[0], normalized_size, *row[2:])
        normalized_loans.append(normalized_row)
        if normalized_size:
            master_sizes.add(str(normalized_size))

    existing_master_sizes = {str(row[0]) for row in pg_master_rows if row[0] is not None}
    missing_master_sizes = sorted(
        {
            str(row[1])
            for row in normalized_loans
            if row[1] is not None and str(row[1]) not in existing_master_sizes
        }
    )

    pg_master_rows.extend((size, 0, None) for size in missing_master_sizes)
    extracted["pin_gauge_lending"] = normalized_loans

    if missing_master_sizes:
        print(f"pin_gauge_master placeholders added: {len(missing_master_sizes)}")


def normalize_loan_size(size: Any, master_sizes: set[str]) -> Any:
    if size is None:
        return None

    text = str(size).strip()
    if text in master_sizes or not NUMERIC_SIZE_PATTERN.fullmatch(text):
        return text

    try:
        formatted = f"{Decimal(text):.3f}"
    except InvalidOperation:
        return text

    if formatted in master_sizes:
        return formatted
    return text


def reset_loan_id_sequence(cursor: Any) -> None:
    cursor.execute(
        """
        SELECT setval(
          pg_get_serial_sequence('"pin_gauge_lending"', 'id'),
          COALESCE((SELECT MAX("id") FROM "pin_gauge_lending"), 1),
          true
        )
        """
    )


def execute_sql_file(cursor: Any, path: Path) -> None:
    cursor.execute(path.read_text(encoding="utf-8"))


def normalize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None
    return value


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def load_psycopg() -> Any:
    try:
        return importlib.import_module("psycopg")
    except ImportError as exc:
        raise RuntimeError("PostgreSQL migration requires psycopg. Run: pip install -r requirements.txt") from exc


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate ピンゲージ管理DB data from Access to PostgreSQL.")
    parser.add_argument("--access-path", help="Full path to ピンゲージ管理DB.accdb.")
    parser.add_argument("--postgres-url", help="PostgreSQL connection URL.")
    parser.add_argument("--schema", default=None, help="Target PostgreSQL schema. Defaults to .env POSTGRES_SCHEMA or public.")
    parser.add_argument("--apply-schema", action="store_true", help="Run database/postgresql/001_schema.sql before import.")
    parser.add_argument("--truncate", action="store_true", help="Truncate target tables before import.")
    parser.add_argument("--dry-run", action="store_true", help="Read Access rows and print counts without writing PostgreSQL.")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
