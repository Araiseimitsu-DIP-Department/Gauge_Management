from __future__ import annotations

import pyodbc

from app.models.pg_master import PgMasterRecord
from app.models.staff import StaffMember


class MasterRowMapper:
    @staticmethod
    def to_pg_master_record(row: pyodbc.Row) -> PgMasterRecord:
        return PgMasterRecord(
            size=str(getattr(row, "サイズ")),
            holding_count=int(getattr(row, "保有数")),
            case_no="" if getattr(row, "ケースNo") is None else str(getattr(row, "ケースNo")),
        )

    @staticmethod
    def to_staff_member(row: pyodbc.Row) -> StaffMember:
        return StaffMember(
            staff_id=str(getattr(row, "担当者ID")),
            name=str(getattr(row, "担当者名")),
            department="" if getattr(row, "部署") is None else str(getattr(row, "部署")),
            kana="" if getattr(row, "かな") is None else str(getattr(row, "かな")),
            visible=(str(getattr(row, "表示")).upper() == "Y") if getattr(row, "表示") is not None else False,
        )
