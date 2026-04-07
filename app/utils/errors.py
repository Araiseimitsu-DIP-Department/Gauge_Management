from __future__ import annotations


class AppError(Exception):
    """Base application error."""


class AppValidationError(AppError):
    """Raised when user input is invalid."""


class AppConfigurationError(AppError):
    """Raised when local configuration is missing or inconsistent."""


class AppDataAccessError(AppError):
    """Raised when database access fails."""

