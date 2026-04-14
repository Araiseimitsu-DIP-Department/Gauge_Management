from __future__ import annotations

from datetime import date

from app.application.dto.loan import LoanRegistrationCommand, LoanSearchCriteria, LoanSummaryDto, LoanUpdateCommand
from app.application.ports.loan_repository import LoanRepositoryPort
from app.shared.errors import ValidationError
from app.utils.validators import NUMBER_MACHINE_PREFIX, validate_lending_registration, validate_lending_search


class LendingUseCase:
    def __init__(self, repository: LoanRepositoryPort) -> None:
        self._repository = repository

    def load_staff_members(self, machine_prefix: str) -> list[object]:
        if not machine_prefix.strip():
            department = None
        else:
            department = "数値" if machine_prefix == NUMBER_MACHINE_PREFIX else "製造"
        return self._repository.fetch_staff_members(department)

    def search_loans(
        self,
        *,
        search_mode: str,
        size_prefix: str,
        machine_prefix: str,
        machine_suffix: str,
        use_size_prefix_match: bool,
    ) -> list[LoanSummaryDto]:
        size_value, machine_code = validate_lending_search(
            search_mode=search_mode,
            size_prefix=size_prefix,
            machine_prefix=machine_prefix,
            machine_suffix=machine_suffix,
        )
        criteria = LoanSearchCriteria(
            size_value=size_value,
            machine_code=machine_code,
            use_size_prefix_match=use_size_prefix_match,
        )
        return self._repository.search_active_loans(criteria)

    def register_loans(
        self,
        *,
        lent_on: date | None,
        machine_prefix: str,
        machine_suffix: str,
        staff_id: str | None,
        gauge_sizes: list[str],
    ) -> list[LoanSummaryDto]:
        machine_code, normalized_sizes = validate_lending_registration(
            lent_on=lent_on,
            machine_prefix=machine_prefix,
            machine_suffix=machine_suffix,
            staff_id=staff_id,
            gauge_sizes=gauge_sizes,
        )
        if lent_on is None or staff_id is None:
            raise ValidationError("貸出日と担当者は必須です。")
        request = LoanRegistrationCommand(
            lent_on=lent_on,
            machine_code=machine_code,
            staff_id=staff_id,
            gauge_sizes=normalized_sizes,
        )
        self._repository.insert_loans(request)
        return self._repository.fetch_registered_loans(
            lent_on=request.lent_on,
            machine_code=request.machine_code,
            staff_id=request.staff_id,
        )

    def update_loan(
        self,
        *,
        loan_id: int,
        lent_on: date | None,
        machine_code: str,
        staff_id: str | None,
        size: str,
    ) -> None:
        if lent_on is None:
            raise ValidationError("貸出日を指定してください。")
        if not machine_code.strip():
            raise ValidationError("機番を指定してください。")
        if not staff_id:
            raise ValidationError("担当者を選択してください。")
        normalized_size = size.strip().upper()
        if not normalized_size:
            raise ValidationError("サイズを入力してください。")

        self._repository.update_loan(
            LoanUpdateCommand(
                loan_id=loan_id,
                lent_on=lent_on,
                machine_code=machine_code.strip().upper(),
                staff_id=staff_id,
                size=normalized_size,
            )
        )

    def delete_loan(self, loan_id: int) -> None:
        self._repository.delete_loan(loan_id)
