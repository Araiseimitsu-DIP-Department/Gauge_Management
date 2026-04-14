from __future__ import annotations

from datetime import date
from typing import Protocol

from app.application.dto.loan import LoanSummaryDto


class OperationRepositoryPort(Protocol):
    def search_returnable_loans(self, machine_code: str) -> list[LoanSummaryDto]:
        ...

    def return_all_loans(self, machine_code: str, returned_on: date, case_no: str) -> int:
        ...

    def return_one_loan(self, loan_id: int, returned_on: date, case_no: str) -> None:
        ...

    def search_confirmation_loans(self, case_no: str) -> list[LoanSummaryDto]:
        ...

    def fetch_confirmation_batches(self) -> list[tuple[str, date | None]]:
        ...

    def confirm_all(self, loan_ids: list[int]) -> int:
        ...

    def confirm_one(self, loan_id: int) -> None:
        ...

