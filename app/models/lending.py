from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LendingSearchCriteria:
    size_value: str | None
    machine_code: str | None
    use_size_prefix_match: bool


@dataclass(frozen=True)
class LendingRegistrationRequest:
    lent_on: date
    machine_code: str
    staff_id: str
    gauge_sizes: list[str]


@dataclass(frozen=True)
class LendingUpdateRequest:
    loan_id: int
    lent_on: date
    machine_code: str
    staff_id: str
    size: str
