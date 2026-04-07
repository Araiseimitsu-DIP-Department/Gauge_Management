from __future__ import annotations

from datetime import date

import pyodbc

from app.config.db_settings import AccessDbSettings
from app.models.loan_record import LoanRecord
from app.repositories.access_connection import open_access_connection


class OperationRepository:
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

        with open_access_connection(self._settings) as connection:
            rows = connection.cursor().execute(sql, machine_code).fetchall()
        return [_map_operation_row(row) for row in rows]

    def return_all_loans(self, machine_code: str, returned_on: date, case_no: str) -> int:
        sql = """
            UPDATE t_貸出
            SET 返却日 = ?, 機番 = ?, 完了フラグ = 'N'
            WHERE 機番 = ? AND 返却日 IS NULL
        """

        returned_machine_code = f"返-{case_no}"
        with open_access_connection(self._settings) as connection:
            cursor = connection.cursor()
            cursor.execute(sql, returned_on, returned_machine_code, machine_code)
            connection.commit()
            return cursor.rowcount if cursor.rowcount != -1 else 0

    def return_one_loan(self, loan_id: int, returned_on: date, case_no: str) -> None:
        sql = """
            UPDATE t_貸出
            SET 返却日 = ?, 機番 = ?, 完了フラグ = 'N'
            WHERE ID = ?
        """

        returned_machine_code = f"返-{case_no}"
        with open_access_connection(self._settings) as connection:
            connection.cursor().execute(sql, returned_on, returned_machine_code, loan_id)
            connection.commit()

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

        with open_access_connection(self._settings) as connection:
            rows = connection.cursor().execute(sql, f"返-{case_no}").fetchall()
        return [_map_operation_row(row) for row in rows]

    def fetch_confirmation_batches(self) -> list[tuple[str, date | None]]:
        sql = """
            SELECT DISTINCT t_貸出.機番, t_貸出.返却日
            FROM t_貸出
            WHERE (t_貸出.完了フラグ = 'N')
               OR (t_貸出.完了フラグ IS NULL AND t_貸出.返却日 IS NOT NULL)
            ORDER BY t_貸出.返却日 DESC
        """

        with open_access_connection(self._settings) as connection:
            rows = connection.cursor().execute(sql).fetchall()

        return [(str(row.機番), row.返却日) for row in rows]

    def confirm_all(self, loan_ids: list[int]) -> int:
        if not loan_ids:
            return 0

        sql = "UPDATE t_貸出 SET 完了フラグ = 'Y' WHERE ID = ?"
        with open_access_connection(self._settings) as connection:
            cursor = connection.cursor()
            cursor.executemany(sql, [(loan_id,) for loan_id in loan_ids])
            connection.commit()
        return len(loan_ids)

    def confirm_one(self, loan_id: int) -> None:
        with open_access_connection(self._settings) as connection:
            connection.cursor().execute(
                "UPDATE t_貸出 SET 完了フラグ = 'Y' WHERE ID = ?",
                loan_id,
            )
            connection.commit()


def _map_operation_row(row: pyodbc.Row) -> LoanRecord:
    return LoanRecord(
        loan_id=int(row.ID),
        size=str(row.サイズ),
        staff_id="" if row.担当者ID is None else str(row.担当者ID),
        staff_name="" if row.担当者名 is None else str(row.担当者名),
        machine_code="" if row.機番 is None else str(row.機番),
        lent_on=row.貸出日,
        returned_on=row.返却日,
        holding_count=None,
        case_no=None if row.ケースNo is None else str(row.ケースNo),
        completion_flag=None if row.完了フラグ is None else str(row.完了フラグ),
    )
