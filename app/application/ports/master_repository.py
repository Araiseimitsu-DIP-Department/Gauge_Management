from __future__ import annotations

from typing import Protocol

from app.application.dto.master import PgMasterDto, StaffMemberDto


class MasterRepositoryPort(Protocol):
    def search_pg_master(self, size_query: str | None = None) -> list[PgMasterDto]:
        ...

    def pg_master_exists(self, size: str) -> bool:
        ...

    def insert_pg_master(self, record: PgMasterDto) -> None:
        ...

    def update_pg_master(self, record: PgMasterDto) -> None:
        ...

    def delete_pg_master(self, size: str) -> None:
        ...

    def fetch_staff_master(self, query: str | None = None) -> list[StaffMemberDto]:
        ...

    def update_staff_member(self, staff: StaffMemberDto) -> None:
        ...

