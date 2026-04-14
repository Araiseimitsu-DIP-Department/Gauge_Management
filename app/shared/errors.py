from __future__ import annotations


class AppError(Exception):
    """Base application error used across layers."""


class ValidationError(AppError):
    """Raised when user input or domain invariants are invalid."""


class ConfigurationError(AppError):
    """Raised when the application or environment is misconfigured."""


class DataAccessError(AppError):
    """Raised when repositories or external systems fail."""

