from __future__ import annotations

import logging
from datetime import date

import pyodbc

from app.config.db_settings import AccessDbSettings
from app.infrastructure.access.mappers.operation_mapper import OperationRowMapper
from app.models.loan_record import LoanRecord
from app.repositories.access_connection import open_access_connection
from app.repositories.errors import RepositoryError

logger = logging.getLogger(__name__)


class AccessOperationRepository:
    def __init__(self, settings: AccessDbSettings) -> None:
        self._settings = settings

    def search_returnable_loans(self, machine_code: str) -> list[LoanRecord]:
        sql = """
            SELECT
                t_貸出.ID,
                t_貸出.サイズ,
                t_貸出.担当者ID,
                t_担当者マスタ.担当者名,
                t_貸出.機番,
                t_貸出.貸出日,
                t_貸出.返却日,
                t_PGマスタ.ケースNo,
                t_貸出.完了フラグ
            FROM
                (t_貸出
                    LEFT JOIN t_担当者マスタ
                        ON t_貸出.担当者ID = t_担当者マスタ.担当者ID)
                LEFT JOIN t_PGマスタ
                    ON t_貸出.サイズ = t_PGマスタ.サイズ
            WHERE
                t_貸出.機番 = ?
                AND t_貸出.完了フラグ IS NULL
                AND t_貸出.返却日 IS NULL
            ORDER BY t_貸出.サイズ
        """

        try:
            with open_access_connection(self._settings) as connection:
                rows = connection.cursor().execute(sql, machine_code).fetchall()
        except pyodbc.Error as exc:
            logger.exception("failed to search returnable loans")
            raise RepositoryError("返却対象の検索に失敗しました。") from exc

        return [OperationRowMapper.to_loan_record(row) for row in rows]

    def return_all_loans(self, machine_code: str, returned_on: date, case_no: str) -> int:
        sql = """
            UPDATE t_貸出
            SET 返却日 = ?, 機番 = ?, 完了フラグ = 'N'
            WHERE 機番 = ? AND 返却日 IS NULL
        """

        returned_machine_code = f"返却{case_no}"
        try:
            with open_access_connection(self._settings) as connection:
                cursor = connection.cursor()
                cursor.execute(sql, returned_on, returned_machine_code, machine_code)
                connection.commit()
                return cursor.rowcount if cursor.rowcount != -1 else 0
        except pyodbc.Error as exc:
            logger.exception("failed to return all loans")
            raise RepositoryError("一括返却に失敗しました。") from exc

    def return_one_loan(self, loan_id: int, returned_on: date, case_no: str) -> None:
        sql = """
            UPDATE t_貸出
            SET 返却日 = ?, 機番 = ?, 完了フラグ = 'N'
            WHERE ID = ?
        """

        returned_machine_code = f"返却{case_no}"
        try:
            with open_access_connection(self._settings) as connection:
                connection.cursor().execute(sql, returned_on, returned_machine_code, loan_id)
                connection.commit()
        except pyodbc.Error as exc:
            logger.exception("failed to return one loan")
            raise RepositoryError("個別返却に失敗しました。") from exc

    def search_confirmation_loans(self, case_no: str) -> list[LoanRecord]:
        sql = """
            SELECT
                t_貸出.ID,
                t_貸出.サイズ,
                t_貸出.担当者ID,
                t_担当者マスタ.担当者名,
                t_貸出.機番,
                t_貸出.貸出日,
                t_貸出.返却日,
                t_PGマスタ.ケースNo,
                t_貸出.完了フラグ
            FROM
                (t_貸出
                    LEFT JOIN t_担当者マスタ
                        ON t_貸出.担当者ID = t_担当者マスタ.担当者ID)
                LEFT JOIN t_PGマスタ
                    ON t_貸出.サイズ = t_PGマスタ.サイズ
            WHERE
                t_貸出.機番 = ?
                AND (t_貸出.完了フラグ IS NULL OR t_貸出.完了フラグ <> 'Y')
            ORDER BY t_貸出.サイズ
        """

        try:
            with open_access_connection(self._settings) as connection:
                rows = connection.cursor().execute(sql, f"返却{case_no}").fetchall()
        except pyodbc.Error as exc:
            logger.exception("failed to search confirmation loans")
            raise RepositoryError("確認対象の検索に失敗しました。") from exc

        return [OperationRowMapper.to_loan_record(row) for row in rows]

    def fetch_confirmation_batches(self) -> list[tuple[str, date | None]]:
        sql = """
            SELECT DISTINCT t_貸出.機番, t_貸出.返却日
            FROM t_貸出
            WHERE (t_貸出.完了フラグ = 'N')
               OR (t_貸出.完了フラグ IS NULL AND t_貸出.返却日 IS NOT NULL)
            ORDER BY t_貸出.返却日 DESC
        """

        try:
            with open_access_connection(self._settings) as connection:
                rows = connection.cursor().execute(sql).fetchall()
        except pyodbc.Error as exc:
            logger.exception("failed to fetch confirmation batches")
            raise RepositoryError("確認待ち一覧の取得に失敗しました。") from exc

        return [(str(getattr(row, "機番")), getattr(row, "返却日")) for row in rows]

    def confirm_all(self, loan_ids: list[int]) -> int:
        if not loan_ids:
            return 0

        sql = "UPDATE t_貸出 SET 完了フラグ = 'Y' WHERE ID = ?"
        try:
            with open_access_connection(self._settings) as connection:
                cursor = connection.cursor()
                cursor.executemany(sql, [(loan_id,) for loan_id in loan_ids])
                connection.commit()
        except pyodbc.Error as exc:
            logger.exception("failed to confirm all loans")
            raise RepositoryError("一括確認に失敗しました。") from exc

        return len(loan_ids)

    def confirm_one(self, loan_id: int) -> None:
        try:
            with open_access_connection(self._settings) as connection:
                connection.cursor().execute(
                    "UPDATE t_貸出 SET 完了フラグ = 'Y' WHERE ID = ?",
                    loan_id,
                )
                connection.commit()
        except pyodbc.Error as exc:
            logger.exception("failed to confirm one loan")
            raise RepositoryError("個別確認に失敗しました。") from exc


def build_access_operation_repository(settings: AccessDbSettings) -> AccessOperationRepository:
    return AccessOperationRepository(settings)

