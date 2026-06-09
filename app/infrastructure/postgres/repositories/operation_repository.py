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
                l."id",
                l."size",
                l."staff_id",
                s."staff_name",
                l."machine_code",
                l."lent_on",
                l."returned_on",
                p."holding_count",
                p."case_no",
                l."completion_flag"
            FROM {self._table("loans")} AS l
            LEFT JOIN {self._table("staff_master")} AS s
                ON l."staff_id" = s."staff_id"
            LEFT JOIN {self._table("pg_master")} AS p
                ON l."size" = p."size"
            WHERE l."machine_code" = %s
              AND l."completion_flag" IS NULL
              AND l."returned_on" IS NULL
            ORDER BY l."size"
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
            UPDATE {self._table("loans")}
            SET "returned_on" = %s, "machine_code" = %s, "completion_flag" = 'N'
            WHERE "machine_code" = %s AND "returned_on" IS NULL
        '''
        returned_machine_code = f"返-{case_no}"

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
            UPDATE {self._table("loans")}
            SET "returned_on" = %s, "machine_code" = %s, "completion_flag" = 'N'
            WHERE "id" = %s
        '''
        returned_machine_code = f"返-{case_no}"
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
                l."id",
                l."size",
                l."staff_id",
                s."staff_name",
                l."machine_code",
                l."lent_on",
                l."returned_on",
                p."holding_count",
                p."case_no",
                l."completion_flag"
            FROM {self._table("loans")} AS l
            LEFT JOIN {self._table("staff_master")} AS s
                ON l."staff_id" = s."staff_id"
            LEFT JOIN {self._table("pg_master")} AS p
                ON l."size" = p."size"
            WHERE l."machine_code" = %s
              AND (l."completion_flag" IS NULL OR l."completion_flag" <> 'Y')
            ORDER BY l."size"
        '''

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (f"返-{case_no}",))
                    rows = cursor.fetchall()
        except Exception as exc:
            logger.exception("failed to search confirmation loans")
            raise RepositoryError("確認対象の読込に失敗しました。") from exc

        return [OperationRowMapper.to_loan_record(row) for row in rows]

    def fetch_confirmation_batches(self) -> list[tuple[str, date | None]]:
        sql = f'''
            SELECT DISTINCT l."machine_code", l."returned_on"
            FROM {self._table("loans")} AS l
            WHERE l."completion_flag" = 'N'
               OR (l."completion_flag" IS NULL AND l."returned_on" IS NOT NULL)
            ORDER BY l."returned_on" DESC
        '''

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql)
                    rows = cursor.fetchall()
        except Exception as exc:
            logger.exception("failed to fetch confirmation batches")
            raise RepositoryError("確認待ち一覧の読込に失敗しました。") from exc

        return [(str(row["machine_code"]), row["returned_on"]) for row in rows]

    def delete_confirmation_batch(self, machine_code: str, returned_on: date | None) -> int:
        sql = f'''
            DELETE FROM {self._table("loans")}
            WHERE "machine_code" = %s
              AND "returned_on" IS NOT DISTINCT FROM %s
              AND (
                "completion_flag" = 'N'
                OR ("completion_flag" IS NULL AND "returned_on" IS NOT NULL)
              )
        '''

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (machine_code, returned_on))
                    deleted_count = cursor.rowcount if cursor.rowcount and cursor.rowcount > 0 else 0
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to delete confirmation batch")
            raise RepositoryError("確認済バッチの削除に失敗しました。") from exc

        return deleted_count

    def confirm_all(self, loan_ids: list[int]) -> int:
        if not loan_ids:
            return 0

        sql = f'UPDATE {self._table("loans")} SET "completion_flag" = \'Y\' WHERE "id" = %s'
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
        sql = f'UPDATE {self._table("loans")} SET "completion_flag" = \'Y\' WHERE "id" = %s'
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
