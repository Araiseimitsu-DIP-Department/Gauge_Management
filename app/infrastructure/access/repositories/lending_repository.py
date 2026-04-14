from __future__ import annotations

import logging
from datetime import date

import pyodbc

from app.config.db_settings import AccessDbSettings
from app.infrastructure.access.mappers.lending_mapper import LendingRowMapper
from app.models.lending import LendingRegistrationRequest, LendingSearchCriteria, LendingUpdateRequest
from app.models.loan_record import LoanRecord
from app.models.staff import StaffMember
from app.repositories.access_connection import open_access_connection
from app.repositories.errors import RepositoryError

logger = logging.getLogger(__name__)


class AccessLendingRepository:
    def __init__(self, settings: AccessDbSettings) -> None:
        self._settings = settings

    def fetch_staff_members(self, department: str | None = None) -> list[StaffMember]:
        sql = """
            SELECT 担当者ID, 担当者名, 部署, かな, 表示
            FROM t_担当者マスタ
            WHERE 表示 = 'Y'
        """
        parameters: list[object] = []
        if department:
            sql += " AND 部署 = ?"
            parameters.append(department)
        sql += " ORDER BY かな"

        try:
            with open_access_connection(self._settings) as connection:
                rows = connection.cursor().execute(sql, *parameters).fetchall()
        except pyodbc.Error as exc:
            logger.exception("failed to fetch staff members")
            raise RepositoryError("担当者マスタの読込に失敗しました。") from exc

        return [LendingRowMapper.to_staff_member(row) for row in rows]

    def search_active_loans(self, criteria: LendingSearchCriteria) -> list[LoanRecord]:
        base_sql = """
            SELECT
                t_貸出.ID,
                t_貸出.サイズ,
                t_貸出.担当者ID,
                t_担当者マスタ.担当者名,
                t_貸出.機番,
                t_貸出.貸出日,
                t_貸出.返却日,
                t_PGマスタ.保有数,
                t_PGマスタ.ケースNo,
                t_貸出.完了フラグ
            FROM
                (t_貸出
                    LEFT JOIN t_担当者マスタ
                        ON t_貸出.担当者ID = t_担当者マスタ.担当者ID)
                LEFT JOIN t_PGマスタ
                    ON t_貸出.サイズ = t_PGマスタ.サイズ
            WHERE
                t_貸出.完了フラグ IS NULL
        """
        parameters: list[object] = []
        if criteria.size_value:
            if criteria.use_size_prefix_match:
                base_sql += " AND t_貸出.サイズ LIKE ?"
                parameters.append(f"{criteria.size_value}%")
            else:
                base_sql += " AND t_貸出.サイズ = ?"
                parameters.append(criteria.size_value)
        elif criteria.machine_code:
            base_sql += " AND t_貸出.機番 = ?"
            parameters.append(criteria.machine_code)
        base_sql += " ORDER BY t_貸出.サイズ"

        try:
            with open_access_connection(self._settings) as connection:
                rows = connection.cursor().execute(base_sql, *parameters).fetchall()
        except pyodbc.Error as exc:
            logger.exception("failed to search active loans")
            raise RepositoryError("貸出一覧の検索に失敗しました。") from exc

        return [LendingRowMapper.to_loan_record(row) for row in rows]

    def insert_loans(self, request: LendingRegistrationRequest) -> int:
        sql = """
            INSERT INTO t_貸出 (サイズ, 担当者ID, 機番, 貸出日)
            VALUES (?, ?, ?, ?)
        """
        parameters = [
            (size, request.staff_id, request.machine_code, request.lent_on)
            for size in request.gauge_sizes
        ]

        try:
            with open_access_connection(self._settings) as connection:
                cursor = connection.cursor()
                cursor.executemany(sql, parameters)
                connection.commit()
        except pyodbc.Error as exc:
            logger.exception("failed to insert loans")
            raise RepositoryError("貸出登録に失敗しました。") from exc

        return len(request.gauge_sizes)

    def fetch_registered_loans(
        self,
        *,
        lent_on: date,
        machine_code: str,
        staff_id: str,
    ) -> list[LoanRecord]:
        sql = """
            SELECT
                t_貸出.ID,
                t_貸出.サイズ,
                t_貸出.担当者ID,
                t_担当者マスタ.担当者名,
                t_貸出.機番,
                t_貸出.貸出日,
                t_貸出.返却日,
                t_PGマスタ.保有数,
                t_PGマスタ.ケースNo,
                t_貸出.完了フラグ
            FROM
                (t_貸出
                    LEFT JOIN t_担当者マスタ
                        ON t_貸出.担当者ID = t_担当者マスタ.担当者ID)
                LEFT JOIN t_PGマスタ
                    ON t_貸出.サイズ = t_PGマスタ.サイズ
            WHERE
                t_貸出.貸出日 = ?
                AND t_貸出.機番 = ?
                AND t_貸出.担当者ID = ?
            ORDER BY t_貸出.サイズ
        """

        try:
            with open_access_connection(self._settings) as connection:
                rows = connection.cursor().execute(sql, lent_on, machine_code, staff_id).fetchall()
        except pyodbc.Error as exc:
            logger.exception("failed to fetch registered loans")
            raise RepositoryError("貸出登録後の再読込に失敗しました。") from exc

        return [LendingRowMapper.to_loan_record(row) for row in rows]

    def update_loan(self, request: LendingUpdateRequest) -> None:
        sql = """
            UPDATE t_貸出
            SET 貸出日 = ?, 機番 = ?, 担当者ID = ?, サイズ = ?
            WHERE ID = ?
        """

        try:
            with open_access_connection(self._settings) as connection:
                connection.cursor().execute(
                    sql,
                    request.lent_on,
                    request.machine_code,
                    request.staff_id,
                    request.size,
                    request.loan_id,
                )
                connection.commit()
        except pyodbc.Error as exc:
            logger.exception("failed to update loan")
            raise RepositoryError("貸出更新に失敗しました。") from exc

    def delete_loan(self, loan_id: int) -> None:
        try:
            with open_access_connection(self._settings) as connection:
                connection.cursor().execute("DELETE FROM t_貸出 WHERE ID = ?", loan_id)
                connection.commit()
        except pyodbc.Error as exc:
            logger.exception("failed to delete loan")
            raise RepositoryError("貸出削除に失敗しました。") from exc


def build_access_lending_repository(settings: AccessDbSettings) -> AccessLendingRepository:
    return AccessLendingRepository(settings)

