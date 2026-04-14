from __future__ import annotations

from datetime import date
from typing import Protocol

from app.application.dto.loan import LoanRegistrationCommand, LoanSearchCriteria, LoanSummaryDto, LoanUpdateCommand


class LoanRepositoryPort(Protocol):
    def fetch_staff_members(self, department: str | None = None) -> list[object]:
        ...

    def search_active_loans(self, criteria: LoanSearchCriteria) -> list[LoanSummaryDto]:
        ...

    def insert_loans(self, request: LoanRegistrationCommand) -> int:
        ...

    def fetch_registered_loans(self, *, lent_on: date, machine_code: str, staff_id: str) -> list[LoanSummaryDto]:
        ...

    def update_loan(self, request: LoanUpdateCommand) -> None:
        ...

    def delete_loan(self, loan_id: int) -> None:
        ...

