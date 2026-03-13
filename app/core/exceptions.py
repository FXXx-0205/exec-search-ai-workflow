from __future__ import annotations


class AppError(Exception):
    pass


class ValidationError(AppError):
    pass


class ExternalServiceError(AppError):
    pass

