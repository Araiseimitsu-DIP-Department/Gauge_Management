from __future__ import annotations

from app.shared.errors import AppError as SharedAppError
from app.shared.errors import ConfigurationError as SharedConfigurationError
from app.shared.errors import DataAccessError as SharedDataAccessError
from app.shared.errors import ValidationError as SharedValidationError


class AppError(SharedAppError):
    """Base application error."""


class AppValidationError(SharedValidationError, AppError):
    """Raised when user input is invalid."""


class AppConfigurationError(SharedConfigurationError, AppError):
    """Raised when local configuration is missing or inconsistent."""


class AppDataAccessError(SharedDataAccessError, AppError):
    """Raised when database access fails."""
