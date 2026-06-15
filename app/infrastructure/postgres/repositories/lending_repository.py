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

PIN_GAUGE_MASTER_TABLE = "pin_gauge_master"
STAFF_MASTER_TABLE = "staff_master"
PIN_GAUGE_LENDING_TABLE = "pin_gauge_lending"


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
            SELECT "staff_id", "staff_name", "department", "kana", "display_flag" AS "visible"
            FROM {self._table(STAFF_MASTER_TABLE)}
            WHERE "display_flag" = %s
        '''
        parameters: list[object] = ["Y"]
        if department:
            sql += ' AND "department" = %s'
            parameters.append(department)
        sql += ' ORDER BY "kana"'

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
                l."id",
                l."size",
                l."staff_id",
                s."staff_name",
                l."machine_no" AS "machine_code",
                l."lent_date" AS "lent_on",
                l."returned_date" AS "returned_on",
                p."owned_quantity" AS "holding_count",
                p."case_no",
                l."completion_flag"
            FROM {self._table(PIN_GAUGE_LENDING_TABLE)} AS l
            LEFT JOIN {self._table(STAFF_MASTER_TABLE)} AS s
                ON l."staff_id" = s."staff_id"
            LEFT JOIN {self._table(PIN_GAUGE_MASTER_TABLE)} AS p
                ON l."size" = p."size"
            WHERE l."completion_flag" IS NULL
        '''
        parameters: list[object] = []
        if criteria.size_value:
            if criteria.use_size_prefix_match:
                sql += ' AND l."size" LIKE %s'
                parameters.append(f"{criteria.size_value}%")
            else:
                sql += ' AND l."size" = %s'
                parameters.append(criteria.size_value)
        elif criteria.machine_code:
            sql += ' AND l."machine_no" = %s'
            parameters.append(criteria.machine_code)
        sql += ' ORDER BY l."size"'

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
            INSERT INTO {self._table(PIN_GAUGE_LENDING_TABLE)}
                ("id", "size", "staff_id", "machine_no", "lent_date")
            VALUES (
                (SELECT COALESCE(MAX(existing."id"), 0) + 1 FROM {self._table(PIN_GAUGE_LENDING_TABLE)} AS existing),
                %s,
                %s,
                %s,
                %s
            )
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
                l."id",
                l."size",
                l."staff_id",
                s."staff_name",
                l."machine_no" AS "machine_code",
                l."lent_date" AS "lent_on",
                l."returned_date" AS "returned_on",
                p."owned_quantity" AS "holding_count",
                p."case_no",
                l."completion_flag"
            FROM {self._table(PIN_GAUGE_LENDING_TABLE)} AS l
            LEFT JOIN {self._table(STAFF_MASTER_TABLE)} AS s
                ON l."staff_id" = s."staff_id"
            LEFT JOIN {self._table(PIN_GAUGE_MASTER_TABLE)} AS p
                ON l."size" = p."size"
            WHERE l."lent_date" = %s
              AND l."machine_no" = %s
              AND l."staff_id" = %s
            ORDER BY l."size"
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
            UPDATE {self._table(PIN_GAUGE_LENDING_TABLE)}
            SET "lent_date" = %s, "machine_no" = %s, "staff_id" = %s, "size" = %s
            WHERE "id" = %s
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
        sql = f'DELETE FROM {self._table(PIN_GAUGE_LENDING_TABLE)} WHERE "id" = %s'
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
