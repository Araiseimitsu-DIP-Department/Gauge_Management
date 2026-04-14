from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from app.models.loan_record import LoanRecord


def _get(row: Any, key: str, default: Any = None) -> Any:
    if isinstance(row, Mapping):
        return row.get(key, default)
    return getattr(row, key, default)


class OperationRowMapper:
    @staticmethod
    def to_loan_record(row: Any) -> LoanRecord:
        return LoanRecord(
            loan_id=int(_get(row, "ID", 0)),
            size=str(_get(row, "サイズ", "")),
            staff_id=str(_get(row, "担当者ID", "")),
            staff_name=str(_get(row, "担当者名", "")),
            machine_code=str(_get(row, "機番", "")),
            lent_on=_normalize_datetime(_get(row, "貸出日")),
            returned_on=_normalize_datetime(_get(row, "返却日")),
            holding_count=_normalize_int(_get(row, "保有数")),
            case_no=_normalize_text(_get(row, "ケースNo")),
            completion_flag=_normalize_text(_get(row, "完了フラグ")),
        )


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_datetime(value: Any) -> date | datetime | None:
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        return value
    return None
