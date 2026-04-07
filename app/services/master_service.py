from __future__ import annotations

import pyodbc

from app.models.pg_master import PgMasterRecord
from app.models.staff import StaffMember
from app.repositories.master_repository import MasterRepository
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError
from app.utils.validators import validate_pg_master_record


class MasterService:
    def __init__(self, repository: MasterRepository) -> None:
        self._repository = repository

    def search_pg_master(self, size_query: str = "") -> list[PgMasterRecord]:
        try:
            return self._repository.search_pg_master(size_query.strip().upper() or None)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("PGマスタ一覧の取得に失敗しました。") from exc

    def save_pg_master(
        self,
        *,
        size: str,
        holding_count: int | None,
        case_no: str,
        is_new: bool,
    ) -> None:
        normalized_size, normalized_holding_count, normalized_case_no = validate_pg_master_record(
            size,
            holding_count,
            case_no,
        )
        record = PgMasterRecord(
            size=normalized_size,
            holding_count=normalized_holding_count,
            case_no=normalized_case_no,
        )

        try:
            if is_new:
                if self._repository.pg_master_exists(record.size):
                    raise AppValidationError("このサイズはマスタに登録済みです。")
                self._repository.insert_pg_master(record)
            else:
                self._repository.update_pg_master(record)
        except AppValidationError:
            raise
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("PGマスタの保存に失敗しました。") from exc

    def delete_pg_master(self, size: str) -> None:
        if not size.strip():
            raise AppValidationError("削除対象のサイズを選択してください。")
        try:
            self._repository.delete_pg_master(size.strip().upper())
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("PGマスタの削除に失敗しました。") from exc

    def search_staff_master(self, query: str = "") -> list[StaffMember]:
        try:
            return self._repository.fetch_staff_master(query.strip() or None)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("担当者マスタ一覧の取得に失敗しました。") from exc

    def update_staff_member(
        self,
        *,
        staff_id: str,
        name: str,
        department: str,
        kana: str,
        visible: bool,
    ) -> None:
        normalized_staff_id = staff_id.strip()
        normalized_name = name.strip()
        normalized_department = department.strip()
        normalized_kana = kana.strip()

        if not normalized_staff_id or not normalized_name:
            raise AppValidationError("担当者IDと担当者名は必ず入力してください。")

        member = StaffMember(
            staff_id=normalized_staff_id,
            name=normalized_name,
            department=normalized_department,
            kana=normalized_kana,
            visible=visible,
        )

        try:
            self._repository.update_staff_member(member)
        except AppConfigurationError:
            raise
        except pyodbc.Error as exc:
            raise AppDataAccessError("担当者マスタの更新に失敗しました。") from exc
