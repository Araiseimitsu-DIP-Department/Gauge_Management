from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LoanSearchCriteria:
    size_value: str | None
    machine_code: str | None
    use_size_prefix_match: bool


@dataclass(frozen=True)
class LoanRegistrationCommand:
    lent_on: date
    machine_code: str
    staff_id: str
    gauge_sizes: list[str]


@dataclass(frozen=True)
class LoanUpdateCommand:
    loan_id: int
    lent_on: date
    machine_code: str
    staff_id: str
    size: str


@dataclass(frozen=True)
class LoanSummaryDto:
    loan_id: int
    size: str
    staff_id: str
    staff_name: str
    machine_code: str
    lent_on: date | None
    returned_on: date | None
    holding_count: int | None
    case_no: str | None = None
    completion_flag: str | None = None

