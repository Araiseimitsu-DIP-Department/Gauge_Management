from __future__ import annotations

import pyodbc

from app.config.db_settings import AccessDbSettings
from app.models.pg_master import PgMasterRecord
from app.models.staff import StaffMember
from app.repositories.access_connection import open_access_connection


class MasterRepository:
    def __init__(self, settings: AccessDbSettings) -> None:
        self._settings = settings

    def search_pg_master(self, size_query: str | None = None) -> list[PgMasterRecord]:
        sql = "SELECT サイズ, 保有数, ケースNo FROM t_PGマスタ"
        parameters: list[object] = []
        if size_query:
            sql += " WHERE サイズ LIKE ?"
            parameters.append(f"{size_query}%")
        sql += " ORDER BY サイズ"

        with open_access_connection(self._settings) as connection:
            rows = connection.cursor().execute(sql, *parameters).fetchall()

        return [
            PgMasterRecord(
                size=str(row.サイズ),
                holding_count=int(row.保有数),
                case_no="" if row.ケースNo is None else str(row.ケースNo),
            )
            for row in rows
        ]

    def pg_master_exists(self, size: str) -> bool:
        sql = "SELECT サイズ FROM t_PGマスタ WHERE サイズ = ?"
        with open_access_connection(self._settings) as connection:
            row = connection.cursor().execute(sql, size).fetchone()
        return row is not None

    def insert_pg_master(self, record: PgMasterRecord) -> None:
        sql = "INSERT INTO t_PGマスタ (サイズ, 保有数, ケースNo) VALUES (?, ?, ?)"
        with open_access_connection(self._settings) as connection:
            connection.cursor().execute(sql, record.size, record.holding_count, record.case_no)
            connection.commit()

    def update_pg_master(self, record: PgMasterRecord) -> None:
        sql = "UPDATE t_PGマスタ SET 保有数 = ?, ケースNo = ? WHERE サイズ = ?"
        with open_access_connection(self._settings) as connection:
            connection.cursor().execute(sql, record.holding_count, record.case_no, record.size)
            connection.commit()

    def delete_pg_master(self, size: str) -> None:
        with open_access_connection(self._settings) as connection:
            connection.cursor().execute("DELETE FROM t_PGマスタ WHERE サイズ = ?", size)
            connection.commit()

    def fetch_staff_master(self, query: str | None = None) -> list[StaffMember]:
        sql = "SELECT 担当者ID, 担当者名, 部署, かな, 表示 FROM t_担当者マスタ"
        parameters: list[object] = []
        if query:
            sql += " WHERE 担当者ID LIKE ? OR 担当者名 LIKE ?"
            parameters.extend([f"{query}%", f"{query}%"])
        sql += " ORDER BY 担当者ID"

        with open_access_connection(self._settings) as connection:
            rows = connection.cursor().execute(sql, *parameters).fetchall()

        return [
            StaffMember(
                staff_id=str(row.担当者ID),
                name=str(row.担当者名),
                department="" if row.部署 is None else str(row.部署),
                kana="" if row.かな is None else str(row.かな),
                visible=(str(row.表示).upper() == "Y") if row.表示 is not None else False,
            )
            for row in rows
        ]

    def update_staff_member(self, staff: StaffMember) -> None:
        sql = """
            UPDATE t_担当者マスタ
            SET 担当者名 = ?, 部署 = ?, かな = ?, 表示 = ?
            WHERE 担当者ID = ?
        """
        visible_value = "Y" if staff.visible else "N"
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
