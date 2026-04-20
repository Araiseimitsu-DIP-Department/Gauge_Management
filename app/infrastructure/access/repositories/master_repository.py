from __future__ import annotations

import logging

import pyodbc

from app.config.db_settings import AccessDbSettings
from app.infrastructure.access.mappers.master_mapper import MasterRowMapper
from app.models.pg_master import PgMasterRecord
from app.models.staff import StaffMember
from app.repositories.access_connection import open_access_connection
from app.repositories.errors import RepositoryError

logger = logging.getLogger(__name__)

STAFF_DEPARTMENT_REPLACEMENTS = {
    "総務": "製造",
    "検査": "数値",
}


class AccessMasterRepository:
    def __init__(self, settings: AccessDbSettings) -> None:
        self._settings = settings

    def search_pg_master(self, size_query: str | None = None) -> list[PgMasterRecord]:
        sql = "SELECT サイズ, 保有数, ケースNo FROM t_PGマスタ"
        parameters: list[object] = []
        if size_query:
            sql += " WHERE サイズ LIKE ?"
            parameters.append(f"{size_query}%")
        sql += " ORDER BY サイズ"

        try:
            with open_access_connection(self._settings) as connection:
                rows = connection.cursor().execute(sql, *parameters).fetchall()
        except pyodbc.Error as exc:
            logger.exception("failed to search pg master")
            raise RepositoryError("PGマスタ一覧の取得に失敗しました。") from exc

        return [MasterRowMapper.to_pg_master_record(row) for row in rows]

    def pg_master_exists(self, size: str) -> bool:
        sql = "SELECT サイズ FROM t_PGマスタ WHERE サイズ = ?"
        try:
            with open_access_connection(self._settings) as connection:
                row = connection.cursor().execute(sql, size).fetchone()
        except pyodbc.Error as exc:
            logger.exception("failed to check pg master existence")
            raise RepositoryError("PGマスタの存在確認に失敗しました。") from exc
        return row is not None

    def insert_pg_master(self, record: PgMasterRecord) -> None:
        sql = "INSERT INTO t_PGマスタ (サイズ, 保有数, ケースNo) VALUES (?, ?, ?)"
        try:
            with open_access_connection(self._settings) as connection:
                connection.cursor().execute(sql, record.size, record.holding_count, record.case_no)
                connection.commit()
        except pyodbc.Error as exc:
            logger.exception("failed to insert pg master")
            raise RepositoryError("PGマスタの保存に失敗しました。") from exc

    def update_pg_master(self, record: PgMasterRecord) -> None:
        sql = "UPDATE t_PGマスタ SET 保有数 = ?, ケースNo = ? WHERE サイズ = ?"
        try:
            with open_access_connection(self._settings) as connection:
                connection.cursor().execute(sql, record.holding_count, record.case_no, record.size)
                connection.commit()
        except pyodbc.Error as exc:
            logger.exception("failed to update pg master")
            raise RepositoryError("PGマスタの更新に失敗しました。") from exc

    def delete_pg_master(self, size: str) -> None:
        try:
            with open_access_connection(self._settings) as connection:
                connection.cursor().execute("DELETE FROM t_PGマスタ WHERE サイズ = ?", size)
                connection.commit()
        except pyodbc.Error as exc:
            logger.exception("failed to delete pg master")
            raise RepositoryError("PGマスタの削除に失敗しました。") from exc

    def fetch_staff_master(self, query: str | None = None) -> list[StaffMember]:
        sql = "SELECT 担当者ID, 担当者名, 部署, かな, 表示 FROM t_担当者マスタ"
        parameters: list[object] = []
        if query:
            sql += " WHERE 担当者ID LIKE ? OR 担当者名 LIKE ?"
            parameters.extend([f"{query}%", f"{query}%"])
        sql += " ORDER BY 担当者ID"

        try:
            with open_access_connection(self._settings) as connection:
                rows = connection.cursor().execute(sql, *parameters).fetchall()
        except pyodbc.Error as exc:
            logger.exception("failed to fetch staff master")
            raise RepositoryError("担当者マスタ一覧の取得に失敗しました。") from exc

        return [MasterRowMapper.to_staff_member(row) for row in rows]

    def update_staff_member(self, staff: StaffMember) -> None:
        sql = """
            UPDATE t_担当者マスタ
            SET 担当者名 = ?, 部署 = ?, かな = ?, 表示 = ?
            WHERE 担当者ID = ?
        """
        visible_value = "Y" if staff.visible else "N"
        try:
            with open_access_connection(self._settings) as connection:
                connection.cursor().execute(
                    sql,
                    staff.name,
                    staff.department,
                    staff.kana,
                    visible_value,
                    staff.staff_id,
                )
                connection.commit()
        except pyodbc.Error as exc:
            logger.exception("failed to update staff member")
            raise RepositoryError("担当者マスタの更新に失敗しました。") from exc

    def normalize_staff_departments(self) -> int:
        updated = 0
        try:
            with open_access_connection(self._settings) as connection:
                cursor = connection.cursor()
                rows = cursor.execute("SELECT 担当者ID, 部署, 担当者名, かな, 表示 FROM t_担当者マスタ").fetchall()
                for row in rows:
                    current_department = "" if row.部署 is None else str(row.部署).strip()
                    replacement = STAFF_DEPARTMENT_REPLACEMENTS.get(current_department)
                    if not replacement or replacement == current_department:
                        continue
                    cursor.execute("UPDATE t_担当者マスタ SET 部署 = ? WHERE 担当者ID = ?", replacement, row.担当者ID)
                    updated += 1
                if updated:
                    connection.commit()
        except pyodbc.Error as exc:
            logger.exception("failed to normalize staff departments")
            raise RepositoryError("担当者マスタの部署更新に失敗しました。") from exc
        return updated


def build_access_master_repository(settings: AccessDbSettings) -> AccessMasterRepository:
    return AccessMasterRepository(settings)
