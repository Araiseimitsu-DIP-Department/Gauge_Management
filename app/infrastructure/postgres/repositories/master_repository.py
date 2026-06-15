from __future__ import annotations

import logging

from app.config.db_settings import PostgresDbSettings
from app.infrastructure.postgres.connection import open_postgres_connection, open_postgres_cursor
from app.infrastructure.postgres.mappers.master_mapper import MasterRowMapper
from app.models.pg_master import PgMasterRecord
from app.models.staff import StaffMember
from app.repositories.errors import RepositoryError

logger = logging.getLogger(__name__)

PIN_GAUGE_MASTER_TABLE = "pin_gauge_master"
STAFF_MASTER_TABLE = "staff_master"
PIN_GAUGE_LENDING_TABLE = "pin_gauge_lending"

STAFF_DEPARTMENT_REPLACEMENTS = {
    "総務": "製造",
    "検査": "数値",
}


class PostgresMasterRepository:
    def __init__(self, settings: PostgresDbSettings) -> None:
        self._settings = settings

    def _table(self, name: str) -> str:
        schema = self._settings.schema.strip()
        if schema:
            return f'"{schema}"."{name}"'
        return f'"{name}"'

    def search_pg_master(self, size_query: str | None = None) -> list[PgMasterRecord]:
        sql = f'SELECT "size", "owned_quantity" AS "holding_count", "case_no" FROM {self._table(PIN_GAUGE_MASTER_TABLE)}'
        parameters: list[object] = []
        if size_query:
            sql += ' WHERE "size" LIKE %s'
            parameters.append(f"{size_query}%")
        sql += ' ORDER BY "size"'

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, tuple(parameters))
                    rows = cursor.fetchall()
        except Exception as exc:
            logger.exception("failed to search pg master")
            raise RepositoryError("PGマスタの読込に失敗しました。") from exc

        return [MasterRowMapper.to_pg_master_record(row) for row in rows]

    def pg_master_exists(self, size: str) -> bool:
        sql = f'SELECT 1 FROM {self._table(PIN_GAUGE_MASTER_TABLE)} WHERE "size" = %s'
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (size,))
                    row = cursor.fetchone()
        except Exception as exc:
            logger.exception("failed to check pg master existence")
            raise RepositoryError("PGマスタの存在確認に失敗しました。") from exc
        return row is not None

    def insert_pg_master(self, record: PgMasterRecord) -> None:
        sql = f'INSERT INTO {self._table(PIN_GAUGE_MASTER_TABLE)} ("size", "owned_quantity", "case_no") VALUES (%s, %s, %s)'
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (record.size, record.holding_count, record.case_no))
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to insert pg master")
            raise RepositoryError("PGマスタの登録に失敗しました。") from exc

    def update_pg_master(self, record: PgMasterRecord) -> None:
        sql = f'''
            UPDATE {self._table(PIN_GAUGE_MASTER_TABLE)}
            SET "owned_quantity" = %s, "case_no" = %s
            WHERE "size" = %s
        '''
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (record.holding_count, record.case_no, record.size))
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to update pg master")
            raise RepositoryError("PGマスタの更新に失敗しました。") from exc

    def count_pg_master_references(self, size: str) -> int:
        sql = f'SELECT COUNT(*) AS "ref_count" FROM {self._table(PIN_GAUGE_LENDING_TABLE)} WHERE "size" = %s'
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (size,))
                    row = cursor.fetchone()
        except Exception as exc:
            logger.exception("failed to count pg master references")
            raise RepositoryError("PGマスタ参照件数の確認に失敗しました。") from exc
        return int(row.get("ref_count", 0) or 0) if row else 0

    def delete_pg_master(self, size: str) -> None:
        sql = f'DELETE FROM {self._table(PIN_GAUGE_MASTER_TABLE)} WHERE "size" = %s'
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (size,))
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to delete pg master")
            raise RepositoryError("PGマスタの削除に失敗しました。") from exc

    def fetch_staff_master(self, query: str | None = None) -> list[StaffMember]:
        sql = f'SELECT "staff_id", "staff_name", "department", "kana", "display_flag" AS "visible" FROM {self._table(STAFF_MASTER_TABLE)}'
        parameters: list[object] = []
        if query:
            sql += ' WHERE "staff_id" LIKE %s OR "staff_name" LIKE %s'
            parameters.extend([f"{query}%", f"{query}%"])
        sql += ' ORDER BY "staff_id"'

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, tuple(parameters))
                    rows = cursor.fetchall()
        except Exception as exc:
            logger.exception("failed to fetch staff master")
            raise RepositoryError("担当者マスタの読込に失敗しました。") from exc

        return [MasterRowMapper.to_staff_member(row) for row in rows]

    def update_staff_member(self, staff: StaffMember) -> None:
        sql = f'''
            UPDATE {self._table(STAFF_MASTER_TABLE)}
            SET "staff_name" = %s, "department" = %s, "kana" = %s, "display_flag" = %s
            WHERE "staff_id" = %s
        '''
        visible_value = "Y" if staff.visible else "N"
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(
                        sql,
                        (staff.name, staff.department, staff.kana, visible_value, staff.staff_id),
                    )
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to update staff member")
            raise RepositoryError("担当者マスタの更新に失敗しました。") from exc

    def normalize_staff_departments(self) -> int:
        updated = 0
        try:
            departments = tuple(STAFF_DEPARTMENT_REPLACEMENTS.keys())
            placeholders = ", ".join(["%s"] * len(departments))
            update_sql = f'''
                UPDATE {self._table(STAFF_MASTER_TABLE)}
                SET "department" = CASE "department"
                    WHEN %s THEN %s
                    WHEN %s THEN %s
                    ELSE "department"
                END
                WHERE "department" IN ({placeholders})
            '''
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(
                        update_sql,
                        ("総務", "製造", "検査", "数値", *departments),
                    )
                    updated = cursor.rowcount if cursor.rowcount and cursor.rowcount > 0 else 0
                connection.commit()  # type: ignore[attr-defined]
        except RepositoryError:
            raise
        except Exception as exc:
            logger.exception("failed to normalize staff departments")
            raise RepositoryError("担当者マスタの部署更新に失敗しました。") from exc
        return updated


def build_postgres_master_repository(settings: PostgresDbSettings) -> PostgresMasterRepository:
    return PostgresMasterRepository(settings)
