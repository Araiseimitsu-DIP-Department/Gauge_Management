from __future__ import annotations

from datetime import date

from app.application.dto.loan import LoanSummaryDto
from app.application.ports.operation_repository import OperationRepositoryPort
from app.shared.errors import ValidationError
from app.utils.validators import build_machine_code, validate_return_case_no


class OperationUseCase:
    def __init__(self, repository: OperationRepositoryPort) -> None:
        self._repository = repository

    def search_returnable_loans(self, machine_prefix: str, machine_suffix: str) -> list[LoanSummaryDto]:
        machine_code = build_machine_code(machine_prefix, machine_suffix)
        if not machine_code:
            raise ValidationError("機番を指定してください。")
        return self._repository.search_returnable_loans(machine_code)

    def return_all_loans(
        self,
        *,
        machine_prefix: str,
        machine_suffix: str,
        case_no: str,
        returned_on: date | None,
        target_count: int,
    ) -> int:
        machine_code = build_machine_code(machine_prefix, machine_suffix)
        if not machine_code:
            raise ValidationError("機番を指定してください。")
        if returned_on is None:
            raise ValidationError("返却日を指定してください。")
        if target_count == 0:
            raise ValidationError("返却対象がありません。")

        normalized_case_no = validate_return_case_no(case_no)
        return self._repository.return_all_loans(machine_code, returned_on, normalized_case_no)

    def return_one_loan(
        self,
        *,
        loan_id: int | None,
        case_no: str,
        returned_on: date | None,
    ) -> None:
        if loan_id is None:
            raise ValidationError("返却対象を選択してください。")
        if returned_on is None:
            raise ValidationError("返却日を指定してください。")

        normalized_case_no = validate_return_case_no(case_no)
        self._repository.return_one_loan(loan_id, returned_on, normalized_case_no)

    def search_confirmation_loans(self, case_no: str) -> list[LoanSummaryDto]:
        normalized_case_no = validate_return_case_no(case_no)
        return self._repository.search_confirmation_loans(normalized_case_no)

    def fetch_confirmation_batches(self) -> list[tuple[str, date | None]]:
        return self._repository.fetch_confirmation_batches()

    def confirm_all(self, loan_ids: list[int]) -> int:
        if not loan_ids:
            raise ValidationError("確認対象がありません。")
        return self._repository.confirm_all(loan_ids)

    def confirm_one(self, loan_id: int | None) -> None:
        if loan_id is None:
            raise ValidationError("確認対象を選択してください。")
        self._repository.confirm_one(loan_id)

