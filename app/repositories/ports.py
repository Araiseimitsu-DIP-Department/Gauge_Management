from __future__ import annotations

from datetime import date
from typing import Protocol

from app.models.lending import LendingRegistrationRequest, LendingSearchCriteria, LendingUpdateRequest
from app.models.loan_record import LoanRecord
from app.models.pg_master import PgMasterRecord
from app.models.staff import StaffMember


class LendingRepositoryPort(Protocol):
    def fetch_staff_members(self, department: str | None = None) -> list[StaffMember]:
        ...

    def search_active_loans(self, criteria: LendingSearchCriteria) -> list[LoanRecord]:
        ...

    def insert_loans(self, request: LendingRegistrationRequest) -> int:
        ...

    def fetch_registered_loans(
        self,
        *,
        lent_on: date,
        machine_code: str,
        staff_id: str,
    ) -> list[LoanRecord]:
        ...

    def update_loan(self, request: LendingUpdateRequest) -> None:
        ...

    def delete_loan(self, loan_id: int) -> None:
        ...


class MasterRepositoryPort(Protocol):
    def search_pg_master(self, size_query: str | None = None) -> list[PgMasterRecord]:
        ...

    def pg_master_exists(self, size: str) -> bool:
        ...

    def insert_pg_master(self, record: PgMasterRecord) -> None:
        ...

    def update_pg_master(self, record: PgMasterRecord) -> None:
        ...

    def delete_pg_master(self, size: str) -> None:
        ...

    def fetch_staff_master(self, query: str | None = None) -> list[StaffMember]:
        ...

    def update_staff_member(self, staff: StaffMember) -> None:
        ...


class OperationRepositoryPort(Protocol):
    def search_returnable_loans(self, machine_code: str) -> list[LoanRecord]:
        ...

    def return_all_loans(self, machine_code: str, returned_on: date, case_no: str) -> int:
        ...

    def return_one_loan(self, loan_id: int, returned_on: date, case_no: str) -> None:
        ...

    def search_confirmation_loans(self, case_no: str) -> list[LoanRecord]:
        ...

    def fetch_confirmation_batches(self) -> list[tuple[str, date | None]]:
        ...

    def confirm_all(self, loan_ids: list[int]) -> int:
        ...

    def confirm_one(self, loan_id: int) -> None:
        ...

