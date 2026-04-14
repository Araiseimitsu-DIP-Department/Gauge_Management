from __future__ import annotations

import pyodbc

from app.models.loan_record import LoanRecord


class OperationRowMapper:
    @staticmethod
    def to_loan_record(row: pyodbc.Row) -> LoanRecord:
        return LoanRecord(
            loan_id=int(getattr(row, "ID")),
            size=str(getattr(row, "サイズ")),
            staff_id="" if getattr(row, "担当者ID") is None else str(getattr(row, "担当者ID")),
            staff_name="" if getattr(row, "担当者名") is None else str(getattr(row, "担当者名")),
            machine_code="" if getattr(row, "機番") is None else str(getattr(row, "機番")),
            lent_on=getattr(row, "貸出日"),
            returned_on=getattr(row, "返却日"),
            holding_count=None,
            case_no=None if getattr(row, "ケースNo") is None else str(getattr(row, "ケースNo")),
            completion_flag=None if getattr(row, "完了フラグ") is None else str(getattr(row, "完了フラグ")),
        )
