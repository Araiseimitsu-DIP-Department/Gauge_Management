from __future__ import annotations

import logging

from app.config.db_settings import PostgresDbSettings
from app.infrastructure.postgres.connection import open_postgres_connection, open_postgres_cursor
from app.infrastructure.postgres.mappers.master_mapper import MasterRowMapper
from app.models.pg_master import PgMasterRecord
from app.models.staff import StaffMember
from app.repositories.errors import RepositoryError

logger = logging.getLogger(__name__)

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
        sql = f'SELECT "サイズ", "保有数", "ケースNo" FROM {self._table("t_PGマスタ")}'
        parameters: list[object] = []
        if size_query:
            sql += ' WHERE "サイズ" LIKE %s'
            parameters.append(f"{size_query}%")
        sql += ' ORDER BY "サイズ"'

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
        sql = f'SELECT 1 FROM {self._table("t_PGマスタ")} WHERE "サイズ" = %s'
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
        sql = f'INSERT INTO {self._table("t_PGマスタ")} ("サイズ", "保有数", "ケースNo") VALUES (%s, %s, %s)'
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
            UPDATE {self._table("t_PGマスタ")}
            SET "保有数" = %s, "ケースNo" = %s
            WHERE "サイズ" = %s
        '''
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (record.holding_count, record.case_no, record.size))
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to update pg master")
            raise RepositoryError("PGマスタの更新に失敗しました。") from exc

    def delete_pg_master(self, size: str) -> None:
        sql = f'DELETE FROM {self._table("t_PGマスタ")} WHERE "サイズ" = %s'
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (size,))
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to delete pg master")
            raise RepositoryError("PGマスタの削除に失敗しました。") from exc

    def fetch_staff_master(self, query: str | None = None) -> list[StaffMember]:
        sql = f'SELECT "担当者ID", "担当者名", "部署", "かな", "表示" FROM {self._table("t_担当者マスタ")}'
        parameters: list[object] = []
        if query:
            sql += ' WHERE "担当者ID" LIKE %s OR "担当者名" LIKE %s'
            parameters.extend([f"{query}%", f"{query}%"])
        sql += ' ORDER BY "担当者ID"'

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
            UPDATE {self._table("t_担当者マスタ")}
            SET "担当者名" = %s, "部署" = %s, "かな" = %s, "表示" = %s
            WHERE "担当者ID" = %s
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
            rows = self.fetch_staff_master(None)
            for staff in rows:
                current_department = staff.department.strip()
                replacement = STAFF_DEPARTMENT_REPLACEMENTS.get(current_department)
                if not replacement or replacement == current_department:
                    continue
                self.update_staff_member(
                    StaffMember(
                        staff_id=staff.staff_id,
                        name=staff.name,
                        department=replacement,
                        kana=staff.kana,
                        visible=staff.visible,
                    )
                )
                updated += 1
        except RepositoryError:
            raise
        except Exception as exc:
            logger.exception("failed to normalize staff departments")
            raise RepositoryError("担当者マスタの部署更新に失敗しました。") from exc
        return updated


def build_postgres_master_repository(settings: PostgresDbSettings) -> PostgresMasterRepository:
    return PostgresMasterRepository(settings)
