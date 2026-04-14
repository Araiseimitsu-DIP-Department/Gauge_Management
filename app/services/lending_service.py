from __future__ import annotations

from datetime import date

from app.application.dto.loan import LoanSummaryDto
from app.application.usecases.lending_usecase import LendingUseCase
from app.models.staff import StaffMember
from app.repositories.errors import RepositoryError
from app.shared.errors import ValidationError
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError


class LendingService:
    def __init__(self, usecase: LendingUseCase) -> None:
        self._usecase = usecase

    def load_staff_members(self, machine_prefix: str) -> list[StaffMember]:
        try:
            return self._usecase.load_staff_members(machine_prefix)
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def search_loans(
        self,
        *,
        search_mode: str,
        size_prefix: str,
        machine_prefix: str,
        machine_suffix: str,
        use_size_prefix_match: bool,
    ) -> list[LoanSummaryDto]:
        try:
            return self._usecase.search_loans(
                search_mode=search_mode,
                size_prefix=size_prefix,
                machine_prefix=machine_prefix,
                machine_suffix=machine_suffix,
                use_size_prefix_match=use_size_prefix_match,
            )
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def register_loans(
        self,
        *,
        lent_on: date | None,
        machine_prefix: str,
        machine_suffix: str,
        staff_id: str | None,
        gauge_sizes: list[str],
    ) -> list[LoanSummaryDto]:
        try:
            return self._usecase.register_loans(
                lent_on=lent_on,
                machine_prefix=machine_prefix,
                machine_suffix=machine_suffix,
                staff_id=staff_id,
                gauge_sizes=gauge_sizes,
            )
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def update_loan(
        self,
        *,
        loan_id: int,
        lent_on: date | None,
        machine_code: str,
        staff_id: str | None,
        size: str,
    ) -> None:
        try:
            self._usecase.update_loan(
                loan_id=loan_id,
                lent_on=lent_on,
                machine_code=machine_code,
                staff_id=staff_id,
                size=size,
            )
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def delete_loan(self, loan_id: int) -> None:
        try:
            self._usecase.delete_loan(loan_id)
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

