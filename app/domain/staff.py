from __future__ import annotations

from dataclasses import dataclass

from app.domain.ids import StaffId


@dataclass(frozen=True)
class Staff:
    staff_id: StaffId
    name: str
    department: str
    kana: str = ""
    visible: bool = True

