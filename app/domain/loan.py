from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.domain.ids import LoanId, StaffId
from app.domain.value_objects import CaseNo, CompletionFlag, MachineCode


@dataclass(frozen=True)
class LoanRecord:
    loan_id: LoanId
    size: str
    staff_id: StaffId
    staff_name: str
    machine_code: MachineCode
    lent_on: date | datetime | None
    returned_on: date | datetime | None
    holding_count: int | None
    case_no: CaseNo | None = None
    completion_flag: CompletionFlag | None = None

