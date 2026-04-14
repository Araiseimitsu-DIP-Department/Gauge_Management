from __future__ import annotations

from datetime import date

from app.application.dto.loan import LoanSummaryDto
from app.application.usecases.operation_usecase import OperationUseCase
from app.models.loan_record import LoanRecord
from app.repositories.errors import RepositoryError
from app.shared.errors import ValidationError
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError


class OperationService:
    def __init__(self, usecase: OperationUseCase) -> None:
        self._usecase = usecase

    def search_returnable_loans(self, machine_prefix: str, machine_suffix: str) -> list[LoanRecord]:
        try:
            rows = self._usecase.search_returnable_loans(machine_prefix, machine_suffix)
            return [
                LoanRecord(
                    loan_id=row.loan_id,
                    size=row.size,
                    staff_id=row.staff_id,
                    staff_name=row.staff_name,
                    machine_code=row.machine_code,
                    lent_on=row.lent_on,
                    returned_on=row.returned_on,
                    holding_count=row.holding_count,
                    case_no=row.case_no,
                    completion_flag=row.completion_flag,
                )
                for row in rows
            ]
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def return_all_loans(
        self,
        *,
        machine_prefix: str,
        machine_suffix: str,
        case_no: str,
        returned_on: date | None,
        target_count: int,
    ) -> int:
        try:
            return self._usecase.return_all_loans(
                machine_prefix=machine_prefix,
                machine_suffix=machine_suffix,
                case_no=case_no,
                returned_on=returned_on,
                target_count=target_count,
            )
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def return_one_loan(
        self,
        *,
        loan_id: int | None,
        case_no: str,
        returned_on: date | None,
    ) -> None:
        try:
            self._usecase.return_one_loan(
                loan_id=loan_id,
                case_no=case_no,
                returned_on=returned_on,
            )
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def search_confirmation_loans(self, case_no: str) -> list[LoanRecord]:
        try:
            rows = self._usecase.search_confirmation_loans(case_no)
            return [
                LoanRecord(
                    loan_id=row.loan_id,
                    size=row.size,
                    staff_id=row.staff_id,
                    staff_name=row.staff_name,
                    machine_code=row.machine_code,
                    lent_on=row.lent_on,
                    returned_on=row.returned_on,
                    holding_count=row.holding_count,
                    case_no=row.case_no,
                    completion_flag=row.completion_flag,
                )
                for row in rows
            ]
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def fetch_confirmation_batches(self) -> list[tuple[str, date | None]]:
        try:
            return self._usecase.fetch_confirmation_batches()
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def confirm_all(self, loan_ids: list[int]) -> int:
        try:
            return self._usecase.confirm_all(loan_ids)
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def confirm_one(self, loan_id: int | None) -> None:
        try:
            self._usecase.confirm_one(loan_id)
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

