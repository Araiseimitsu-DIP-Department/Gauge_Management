from __future__ import annotations

import logging
from datetime import date

from app.config.db_settings import PostgresDbSettings
from app.infrastructure.postgres.connection import open_postgres_connection, open_postgres_cursor
from app.infrastructure.postgres.mappers.operation_mapper import OperationRowMapper
from app.models.loan_record import LoanRecord
from app.repositories.errors import RepositoryError

logger = logging.getLogger(__name__)


class PostgresOperationRepository:
    def __init__(self, settings: PostgresDbSettings) -> None:
        self._settings = settings

    def _table(self, name: str) -> str:
        schema = self._settings.schema.strip()
        if schema:
            return f'"{schema}"."{name}"'
        return f'"{name}"'

    def search_returnable_loans(self, machine_code: str) -> list[LoanRecord]:
        sql = f'''
            SELECT
                l."ID",
                l."サイズ",
                l."担当者ID",
                s."担当者名",
                l."機番",
                l."貸出日",
                l."返却日",
                p."保有数",
                p."ケースNo",
                l."完了フラグ"
            FROM {self._table("t_貸出")} AS l
            LEFT JOIN {self._table("t_担当者マスタ")} AS s
                ON l."担当者ID" = s."担当者ID"
            LEFT JOIN {self._table("t_PGマスタ")} AS p
                ON l."サイズ" = p."サイズ"
            WHERE l."機番" = %s
              AND l."完了フラグ" IS NULL
              AND l."返却日" IS NULL
            ORDER BY l."サイズ"
        '''

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (machine_code,))
                    rows = cursor.fetchall()
        except Exception as exc:
            logger.exception("failed to search returnable loans")
            raise RepositoryError("返却対象の読込に失敗しました。") from exc

        return [OperationRowMapper.to_loan_record(row) for row in rows]

    def return_all_loans(self, machine_code: str, returned_on: date, case_no: str) -> int:
        sql = f'''
            UPDATE {self._table("t_貸出")}
            SET "返却日" = %s, "機番" = %s, "完了フラグ" = 'N'
            WHERE "機番" = %s AND "返却日" IS NULL
        '''
        returned_machine_code = f"返却{case_no}"

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (returned_on, returned_machine_code, machine_code))
                    updated_count = cursor.rowcount if cursor.rowcount and cursor.rowcount > 0 else 0
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to return all loans")
            raise RepositoryError("一括返却に失敗しました。") from exc

        return updated_count

    def return_one_loan(self, loan_id: int, returned_on: date, case_no: str) -> None:
        sql = f'''
            UPDATE {self._table("t_貸出")}
            SET "返却日" = %s, "機番" = %s, "完了フラグ" = 'N'
            WHERE "ID" = %s
        '''
        returned_machine_code = f"返却{case_no}"
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (returned_on, returned_machine_code, loan_id))
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to return one loan")
            raise RepositoryError("個別返却に失敗しました。") from exc

    def search_confirmation_loans(self, case_no: str) -> list[LoanRecord]:
        sql = f'''
            SELECT
                l."ID",
                l."サイズ",
                l."担当者ID",
                s."担当者名",
                l."機番",
                l."貸出日",
                l."返却日",
                p."保有数",
                p."ケースNo",
                l."完了フラグ"
            FROM {self._table("t_貸出")} AS l
            LEFT JOIN {self._table("t_担当者マスタ")} AS s
                ON l."担当者ID" = s."担当者ID"
            LEFT JOIN {self._table("t_PGマスタ")} AS p
                ON l."サイズ" = p."サイズ"
            WHERE l."機番" = %s
              AND (l."完了フラグ" IS NULL OR l."完了フラグ" <> 'Y')
            ORDER BY l."サイズ"
        '''

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (f"返却{case_no}",))
                    rows = cursor.fetchall()
        except Exception as exc:
            logger.exception("failed to search confirmation loans")
            raise RepositoryError("確認対象の読込に失敗しました。") from exc

        return [OperationRowMapper.to_loan_record(row) for row in rows]

    def fetch_confirmation_batches(self) -> list[tuple[str, date | None]]:
        sql = f'''
            SELECT DISTINCT l."機番", l."返却日"
            FROM {self._table("t_貸出")} AS l
            WHERE l."完了フラグ" = 'N'
               OR (l."完了フラグ" IS NULL AND l."返却日" IS NOT NULL)
            ORDER BY l."返却日" DESC
        '''

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql)
                    rows = cursor.fetchall()
        except Exception as exc:
            logger.exception("failed to fetch confirmation batches")
            raise RepositoryError("確認待ち一覧の読込に失敗しました。") from exc

        return [(str(row["機番"]), row["返却日"]) for row in rows]

    def confirm_all(self, loan_ids: list[int]) -> int:
        if not loan_ids:
            return 0

        sql = f'UPDATE {self._table("t_貸出")} SET "完了フラグ" = \'Y\' WHERE "ID" = %s'
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    for loan_id in loan_ids:
                        cursor.execute(sql, (loan_id,))
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to confirm all loans")
            raise RepositoryError("一括確認に失敗しました。") from exc

        return len(loan_ids)

    def confirm_one(self, loan_id: int) -> None:
        sql = f'UPDATE {self._table("t_貸出")} SET "完了フラグ" = \'Y\' WHERE "ID" = %s'
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (loan_id,))
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to confirm one loan")
            raise RepositoryError("個別確認に失敗しました。") from exc


def build_postgres_operation_repository(settings: PostgresDbSettings) -> PostgresOperationRepository:
    return PostgresOperationRepository(settings)
