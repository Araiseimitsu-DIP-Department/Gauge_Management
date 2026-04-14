from __future__ import annotations

import pyodbc

from app.models.loan_record import LoanRecord
from app.models.staff import StaffMember


class LendingRowMapper:
    @staticmethod
    def to_staff_member(row: pyodbc.Row) -> StaffMember:
        return StaffMember(
            staff_id=str(getattr(row, "担当者ID")),
            name=str(getattr(row, "担当者名")),
            department="" if getattr(row, "部署") is None else str(getattr(row, "部署")),
            kana="" if getattr(row, "かな") is None else str(getattr(row, "かな")),
            visible=(str(getattr(row, "表示")).upper() == "Y") if getattr(row, "表示") is not None else True,
        )

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
            holding_count=None if getattr(row, "保有数") is None else int(getattr(row, "保有数")),
            case_no=_get_optional_str(row, "ケースNo"),
            completion_flag=_get_optional_str(row, "完了フラグ"),
        )


def _get_optional_str(row: pyodbc.Row, column_name: str) -> str | None:
    value = getattr(row, column_name, None)
    return None if value is None else str(value)

