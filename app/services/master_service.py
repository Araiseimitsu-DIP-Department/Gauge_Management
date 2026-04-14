from __future__ import annotations

from app.application.dto.master import PgMasterDto, StaffMemberDto
from app.application.usecases.master_usecase import MasterUseCase
from app.models.pg_master import PgMasterRecord
from app.models.staff import StaffMember
from app.repositories.errors import RepositoryError
from app.shared.errors import ValidationError
from app.utils.errors import AppConfigurationError, AppDataAccessError, AppValidationError


class MasterService:
    def __init__(self, usecase: MasterUseCase) -> None:
        self._usecase = usecase

    def search_pg_master(self, size_query: str = "") -> list[PgMasterRecord]:
        try:
            rows = self._usecase.search_pg_master(size_query)
            return [PgMasterRecord(size=row.size, holding_count=row.holding_count, case_no=row.case_no) for row in rows]
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def save_pg_master(
        self,
        *,
        size: str,
        holding_count: int | None,
        case_no: str,
        is_new: bool,
    ) -> None:
        try:
            self._usecase.save_pg_master(
                size=size,
                holding_count=holding_count,
                case_no=case_no,
                is_new=is_new,
            )
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def delete_pg_master(self, size: str) -> None:
        try:
            self._usecase.delete_pg_master(size)
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def search_staff_master(self, query: str = "") -> list[StaffMember]:
        try:
            rows = self._usecase.search_staff_master(query)
            return [
                StaffMember(
                    staff_id=row.staff_id,
                    name=row.name,
                    department=row.department,
                    kana=row.kana,
                    visible=row.visible,
                )
                for row in rows
            ]
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

    def update_staff_member(
        self,
        *,
        staff_id: str,
        name: str,
        department: str,
        kana: str,
        visible: bool,
    ) -> None:
        try:
            self._usecase.update_staff_member(
                staff_id=staff_id,
                name=name,
                department=department,
                kana=kana,
                visible=visible,
            )
        except AppConfigurationError:
            raise
        except ValidationError as exc:
            raise AppValidationError(str(exc)) from exc
        except RepositoryError as exc:
            raise AppDataAccessError(str(exc)) from exc

