from __future__ import annotations

from datetime import date

import pyodbc

from app.config.db_settings import AccessDbSettings
from app.models.lending import LendingRegistrationRequest, LendingSearchCriteria, LendingUpdateRequest
from app.models.loan_record import LoanRecord
from app.models.staff import StaffMember
from app.repositories.access_connection import open_access_connection


class LendingRepository:
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

        with open_access_connection(self._settings) as connection:
            cursor = connection.cursor()
            rows = cursor.execute(sql, *parameters).fetchall()

        return [
            StaffMember(
                staff_id=str(row.担当者ID),
                name=str(row.担当者名),
                department=str(row.部署),
                kana="" if row.かな is None else str(row.かな),
                visible=(str(row.表示).upper() == "Y") if row.表示 is not None else True,
            )
            for row in rows
        ]

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
                t_PGマスタ.保有数
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

        with open_access_connection(self._settings) as connection:
            cursor = connection.cursor()
            rows = cursor.execute(base_sql, *parameters).fetchall()

        return [self._map_loan_record(row) for row in rows]

    def insert_loans(self, request: LendingRegistrationRequest) -> int:
        sql = """
            INSERT INTO t_貸出 (サイズ, 担当者ID, 機番, 貸出日)
            VALUES (?, ?, ?, ?)
        """
        parameters = [
            (
                size,
                request.staff_id,
                request.machine_code,
                request.lent_on,
            )
            for size in request.gauge_sizes
        ]

        with open_access_connection(self._settings) as connection:
            cursor = connection.cursor()
            cursor.executemany(sql, parameters)
            connection.commit()

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
                t_PGマスタ.保有数
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

        with open_access_connection(self._settings) as connection:
            cursor = connection.cursor()
            rows = cursor.execute(sql, lent_on, machine_code, staff_id).fetchall()

        return [self._map_loan_record(row) for row in rows]

    def update_loan(self, request: LendingUpdateRequest) -> None:
        sql = """
            UPDATE t_貸出
            SET 貸出日 = ?, 機番 = ?, 担当者ID = ?, サイズ = ?
            WHERE ID = ?
        """
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

    def delete_loan(self, loan_id: int) -> None:
        with open_access_connection(self._settings) as connection:
            connection.cursor().execute("DELETE FROM t_貸出 WHERE ID = ?", loan_id)
            connection.commit()

    @staticmethod
    def _map_loan_record(row: pyodbc.Row) -> LoanRecord:
        return LoanRecord(
            loan_id=int(row.ID),
            size=str(row.サイズ),
            staff_id=str(row.担当者ID),
            staff_name="" if row.担当者名 is None else str(row.担当者名),
            machine_code="" if row.機番 is None else str(row.機番),
            lent_on=row.貸出日,
            returned_on=row.返却日,
            holding_count=None if row.保有数 is None else int(row.保有数),
            case_no=_get_optional_str(row, "ケースNo"),
            completion_flag=_get_optional_str(row, "完了フラグ"),
        )


def _get_optional_str(row: pyodbc.Row, column_name: str) -> str | None:
    try:
        value = getattr(row, column_name)
    except AttributeError:
        return None
    return None if value is None else str(value)
