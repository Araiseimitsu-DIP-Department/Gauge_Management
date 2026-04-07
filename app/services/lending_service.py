from __future__ import annotations

from datetime import date

import pyodbc

from app.models.lending import LendingRegistrationRequest, LendingSearchCriteria, LendingUpdateRequest
from app.models.loan_record import LoanRecord
from app.models.staff import StaffMember
from app.repositories.lending_repository import LendingRepository
from app.utils.errors import (
    AppConfigurationError,
    AppDataAccessError,
    AppValidationError,
)
from app.utils.validators import (
    NUMBER_MACHINE_PREFIX,
    validate_lending_registration,
    validate_lending_search,
)


class LendingService:
    def __init__(self, repository: LendingRepository) -> None:
        self._repository = repository

    def load_staff_members(self, machine_prefix: str) -> list[StaffMember]:
        if not machine_prefix.strip():
            department = None
        else:
            department = "数値" if machine_prefix == NUMBER_MACHINE_PREFIX else "製造"

        try:
            return self._repository.fetch_staff_members(department)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("担当者マスタの読込に失敗しました。") from exc

    def search_loans(
        self,
        *,
        search_mode: str,
        size_prefix: str,
        machine_prefix: str,
        machine_suffix: str,
        use_size_prefix_match: bool,
    ) -> list[LoanRecord]:
        normalized_size_value, machine_code = validate_lending_search(
            search_mode=search_mode,
            size_prefix=size_prefix,
            machine_prefix=machine_prefix,
            machine_suffix=machine_suffix,
        )

        try:
            return self._repository.search_active_loans(
                LendingSearchCriteria(
                    size_value=normalized_size_value,
                    machine_code=machine_code,
                    use_size_prefix_match=use_size_prefix_match,
                )
            )
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("貸出一覧の検索に失敗しました。") from exc

    def register_loans(
        self,
        *,
        lent_on: date | None,
        machine_prefix: str,
        machine_suffix: str,
        staff_id: str | None,
        gauge_sizes: list[str],
    ) -> list[LoanRecord]:
        machine_code, normalized_sizes = validate_lending_registration(
            lent_on=lent_on,
            machine_prefix=machine_prefix,
            machine_suffix=machine_suffix,
            staff_id=staff_id,
            gauge_sizes=gauge_sizes,
        )

        assert lent_on is not None
        assert staff_id is not None

        request = LendingRegistrationRequest(
            lent_on=lent_on,
            machine_code=machine_code,
            staff_id=staff_id,
            gauge_sizes=normalized_sizes,
        )

        try:
            self._repository.insert_loans(request)
            return self._repository.fetch_registered_loans(
                lent_on=request.lent_on,
                machine_code=request.machine_code,
                staff_id=request.staff_id,
            )
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("貸出登録に失敗しました。") from exc

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
            raise AppValidationError("貸出日を入力してください。")
        if not machine_code.strip():
            raise AppValidationError("機番を入力してください。")
        if not staff_id:
            raise AppValidationError("担当者を選択してください。")
        normalized_size = size.strip().upper()
        if not normalized_size:
            raise AppValidationError("サイズを入力してください。")

        request = LendingUpdateRequest(
            loan_id=loan_id,
            lent_on=lent_on,
            machine_code=machine_code.strip().upper(),
            staff_id=staff_id,
            size=normalized_size,
        )

        try:
            self._repository.update_loan(request)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("貸出更新に失敗しました。") from exc

    def delete_loan(self, loan_id: int) -> None:
        try:
            self._repository.delete_loan(loan_id)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("貸出削除に失敗しました。") from exc
