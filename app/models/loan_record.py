from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class LoanRecord:
    loan_id: int
    size: str
    staff_id: str
    staff_name: str
    machine_code: str
    lent_on: date | datetime | None
    returned_on: date | datetime | None
    holding_count: int | None
    case_no: str | None = None
    completion_flag: str | None = None
