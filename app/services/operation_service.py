from __future__ import annotations

from datetime import date

import pyodbc

from app.models.loan_record import LoanRecord
from app.repositories.operation_repository import OperationRepository
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError
from app.utils.validators import build_machine_code, validate_return_case_no


class OperationService:
    def __init__(self, repository: OperationRepository) -> None:
        self._repository = repository

    def search_returnable_loans(self, machine_prefix: str, machine_suffix: str) -> list[LoanRecord]:
        machine_code = build_machine_code(machine_prefix, machine_suffix)
        if not machine_code:
            raise AppValidationError("機番を入力してください。")

        try:
            return self._repository.search_returnable_loans(machine_code)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("返却対象の検索に失敗しました。") from exc

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
            raise AppValidationError("機番を入力してください。")
        if returned_on is None:
            raise AppValidationError("返却日を入力してください。")
        if target_count == 0:
            raise AppValidationError("返却対象がありません。")

        normalized_case_no = validate_return_case_no(case_no)

        try:
            return self._repository.return_all_loans(machine_code, returned_on, normalized_case_no)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("一括返却に失敗しました。") from exc

    def return_one_loan(
        self,
        *,
        loan_id: int | None,
        case_no: str,
        returned_on: date | None,
    ) -> None:
        if loan_id is None:
            raise AppValidationError("返却対象を選択してください。")
        if returned_on is None:
            raise AppValidationError("返却日を入力してください。")

        normalized_case_no = validate_return_case_no(case_no)

        try:
            self._repository.return_one_loan(loan_id, returned_on, normalized_case_no)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("個別返却に失敗しました。") from exc

    def search_confirmation_loans(self, case_no: str) -> list[LoanRecord]:
        normalized_case_no = validate_return_case_no(case_no)
        try:
            return self._repository.search_confirmation_loans(normalized_case_no)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("確認対象の検索に失敗しました。") from exc

    def fetch_confirmation_batches(self) -> list[tuple[str, date | None]]:
        try:
            return self._repository.fetch_confirmation_batches()
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("確認待ち一覧の取得に失敗しました。") from exc

    def confirm_all(self, loan_ids: list[int]) -> int:
        if not loan_ids:
            raise AppValidationError("確認対象がありません。")
        try:
            return self._repository.confirm_all(loan_ids)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("一括確認に失敗しました。") from exc

    def confirm_one(self, loan_id: int | None) -> None:
        if loan_id is None:
            raise AppValidationError("確認対象を選択してください。")
        try:
            self._repository.confirm_one(loan_id)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("個別確認に失敗しました。") from exc

