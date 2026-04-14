from __future__ import annotations

from dataclasses import dataclass

from app.application.ports.loan_repository import LoanRepositoryPort
from app.application.ports.master_repository import MasterRepositoryPort
from app.application.ports.operation_repository import OperationRepositoryPort
from app.config.app_settings import AppSettings
from app.infrastructure.access.repositories.lending_repository import build_access_lending_repository
from app.infrastructure.access.repositories.master_repository import build_access_master_repository
from app.infrastructure.access.repositories.operation_repository import build_access_operation_repository
from app.infrastructure.postgres.repositories.lending_repository import PostgresLendingRepository
from app.infrastructure.postgres.repositories.master_repository import PostgresMasterRepository
from app.infrastructure.postgres.repositories.operation_repository import PostgresOperationRepository
from app.shared.errors import ConfigurationError


@dataclass(frozen=True)
class RepositoryBundle:
    lending: LoanRepositoryPort
    master: MasterRepositoryPort
    operation: OperationRepositoryPort


def build_repository_bundle(settings: AppSettings) -> RepositoryBundle:
    backend = settings.database_backend
    if backend == "access":
        return RepositoryBundle(
            lending=build_access_lending_repository(settings.access_db),
            master=build_access_master_repository(settings.access_db),
            operation=build_access_operation_repository(settings.access_db),
        )
    if backend == "postgres":
        return RepositoryBundle(
            lending=PostgresLendingRepository(settings.postgres_db),
            master=PostgresMasterRepository(settings.postgres_db),
            operation=PostgresOperationRepository(settings.postgres_db),
        )
    raise ConfigurationError(f"Unsupported DB_BACKEND: {backend}")

