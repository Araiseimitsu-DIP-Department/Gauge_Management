from __future__ import annotations

from app.application.dto.master import PgMasterDto, StaffMemberDto
from app.application.ports.master_repository import MasterRepositoryPort
from app.shared.errors import ValidationError
from app.utils.validators import validate_pg_master_record


class MasterUseCase:
    def __init__(self, repository: MasterRepositoryPort) -> None:
        self._repository = repository

    def search_pg_master(self, size_query: str = "") -> list[PgMasterDto]:
        return self._repository.search_pg_master(size_query.strip().upper() or None)

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
        record = PgMasterDto(
            size=normalized_size,
            holding_count=normalized_holding_count,
            case_no=normalized_case_no,
        )
        if is_new:
            if self._repository.pg_master_exists(record.size):
                raise ValidationError("このサイズは既にマスタに登録されています。")
            self._repository.insert_pg_master(record)
        else:
            self._repository.update_pg_master(record)

    def delete_pg_master(self, size: str) -> None:
        if not size.strip():
            raise ValidationError("削除対象のサイズを指定してください。")
        self._repository.delete_pg_master(size.strip().upper())

    def search_staff_master(self, query: str = "") -> list[StaffMemberDto]:
        return self._repository.fetch_staff_master(query.strip() or None)

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
            raise ValidationError("担当者IDと担当者名は必須です。")

        self._repository.update_staff_member(
            StaffMemberDto(
                staff_id=normalized_staff_id,
                name=normalized_name,
                department=normalized_department,
                kana=normalized_kana,
                visible=visible,
            )
        )

