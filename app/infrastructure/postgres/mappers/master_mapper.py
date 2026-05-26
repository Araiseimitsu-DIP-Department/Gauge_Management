from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.models.pg_master import PgMasterRecord
from app.models.staff import StaffMember


def _get(row: Any, key: str, default: Any = None) -> Any:
    if isinstance(row, Mapping):
        return row.get(key, default)
    return getattr(row, key, default)


class MasterRowMapper:
    @staticmethod
    def to_pg_master_record(row: Any) -> PgMasterRecord:
        return PgMasterRecord(
            size=str(_get(row, "size", "")),
            holding_count=int(_get(row, "holding_count", 0) or 0),
            case_no=str(_get(row, "case_no", "")),
        )

    @staticmethod
    def to_staff_member(row: Any) -> StaffMember:
        visible_value = _get(row, "visible")
        return StaffMember(
            staff_id=str(_get(row, "staff_id", "")),
            name=str(_get(row, "staff_name", "")),
            department=str(_get(row, "department", "")),
            kana=str(_get(row, "kana", "")),
            visible=str(visible_value).upper() == "Y" if visible_value is not None else True,
        )
