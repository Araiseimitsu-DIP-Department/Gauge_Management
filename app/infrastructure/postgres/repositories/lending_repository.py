from __future__ import annotations

import logging
from datetime import date

from app.config.db_settings import PostgresDbSettings
from app.infrastructure.postgres.connection import open_postgres_connection, open_postgres_cursor
from app.infrastructure.postgres.mappers.lending_mapper import LendingRowMapper
from app.models.lending import LendingRegistrationRequest, LendingSearchCriteria, LendingUpdateRequest
from app.models.loan_record import LoanRecord
from app.models.staff import StaffMember
from app.repositories.errors import RepositoryError

logger = logging.getLogger(__name__)


class PostgresLendingRepository:
    def __init__(self, settings: PostgresDbSettings) -> None:
        self._settings = settings

    def _table(self, name: str) -> str:
        schema = self._settings.schema.strip()
        if schema:
            return f'"{schema}"."{name}"'
        return f'"{name}"'

    def fetch_staff_members(self, department: str | None = None) -> list[StaffMember]:
        sql = f'''
            SELECT "担当者ID", "担当者名", "部署", "かな", "表示"
            FROM {self._table("t_担当者マスタ")}
            WHERE "表示" = %s
        '''
        parameters: list[object] = ["Y"]
        if department:
            sql += ' AND "部署" = %s'
            parameters.append(department)
        sql += ' ORDER BY "かな"'

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, tuple(parameters))
                    rows = cursor.fetchall()
        except Exception as exc:
            logger.exception("failed to fetch staff members")
            raise RepositoryError("担当者マスタの読込に失敗しました。") from exc

        return [LendingRowMapper.to_staff_member(row) for row in rows]

    def search_active_loans(self, criteria: LendingSearchCriteria) -> list[LoanRecord]:
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
            WHERE l."完了フラグ" IS NULL
        '''
        parameters: list[object] = []
        if criteria.size_value:
            if criteria.use_size_prefix_match:
                sql += ' AND l."サイズ" LIKE %s'
                parameters.append(f"{criteria.size_value}%")
            else:
                sql += ' AND l."サイズ" = %s'
                parameters.append(criteria.size_value)
        elif criteria.machine_code:
            sql += ' AND l."機番" = %s'
            parameters.append(criteria.machine_code)
        sql += ' ORDER BY l."サイズ"'

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, tuple(parameters))
                    rows = cursor.fetchall()
        except Exception as exc:
            logger.exception("failed to search active loans")
            raise RepositoryError("貸出一覧の読込に失敗しました。") from exc

        return [LendingRowMapper.to_loan_record(row) for row in rows]

    def insert_loans(self, request: LendingRegistrationRequest) -> int:
        sql = f'''
            INSERT INTO {self._table("t_貸出")} ("サイズ", "担当者ID", "機番", "貸出日")
            VALUES (%s, %s, %s, %s)
        '''
        parameters = [
            (size, request.staff_id, request.machine_code, request.lent_on)
            for size in request.gauge_sizes
        ]

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    for parameter in parameters:
                        cursor.execute(sql, parameter)
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
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
            WHERE l."貸出日" = %s
              AND l."機番" = %s
              AND l."担当者ID" = %s
            ORDER BY l."サイズ"
        '''

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (lent_on, machine_code, staff_id))
                    rows = cursor.fetchall()
        except Exception as exc:
            logger.exception("failed to fetch registered loans")
            raise RepositoryError("貸出登録後の読込に失敗しました。") from exc

        return [LendingRowMapper.to_loan_record(row) for row in rows]

    def update_loan(self, request: LendingUpdateRequest) -> None:
        sql = f'''
            UPDATE {self._table("t_貸出")}
            SET "貸出日" = %s, "機番" = %s, "担当者ID" = %s, "サイズ" = %s
            WHERE "ID" = %s
        '''

        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(
                        sql,
                        (
                            request.lent_on,
                            request.machine_code,
                            request.staff_id,
                            request.size,
                            request.loan_id,
                        ),
                    )
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to update loan")
            raise RepositoryError("貸出更新に失敗しました。") from exc

    def delete_loan(self, loan_id: int) -> None:
        sql = f'DELETE FROM {self._table("t_貸出")} WHERE "ID" = %s'
        try:
            with open_postgres_connection(self._settings) as connection:
                with open_postgres_cursor(connection) as cursor:
                    cursor.execute(sql, (loan_id,))
                connection.commit()  # type: ignore[attr-defined]
        except Exception as exc:
            logger.exception("failed to delete loan")
            raise RepositoryError("貸出削除に失敗しました。") from exc


def build_postgres_lending_repository(settings: PostgresDbSettings) -> PostgresLendingRepository:
    return PostgresLendingRepository(settings)
