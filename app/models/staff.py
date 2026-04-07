from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StaffMember:
    staff_id: str
    name: str
    department: str
    kana: str = ""
    visible: bool = True
