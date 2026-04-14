from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PgMasterDto:
    size: str
    holding_count: int
    case_no: str


@dataclass(frozen=True)
class StaffMemberDto:
    staff_id: str
    name: str
    department: str
    kana: str = ""
    visible: bool = True

