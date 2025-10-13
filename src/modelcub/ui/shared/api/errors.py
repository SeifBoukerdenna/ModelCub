"""Shared API error definitions."""
from typing import Optional, Dict, Any


class ErrorCode:
    """Standardized error codes."""

    # Generic errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    BAD_REQUEST = "BAD_REQUEST"

    # Project errors
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    PROJECT_ALREADY_EXISTS = "PROJECT_ALREADY_EXISTS"
    PROJECT_INVALID = "PROJECT_INVALID"
    PROJECT_LOAD_FAILED = "PROJECT_LOAD_FAILED"

    # Dataset errors
    DATASET_NOT_FOUND = "DATASET_NOT_FOUND"
    DATASET_ALREADY_EXISTS = "DATASET_ALREADY_EXISTS"
    DATASET_IMPORT_FAILED = "DATASET_IMPORT_FAILED"
    DATASET_INVALID = "DATASET_INVALID"

    # Model errors
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    TRAINING_FAILED = "TRAINING_FAILED"

    # File errors
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"


class APIError(Exception):
    """Base API error."""

    def __init__(
        self,
        message: str,
        code: str = ErrorCode.INTERNAL_ERROR,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(self, message: str, code: str = ErrorCode.NOT_FOUND, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, 404, details)


class ValidationError(APIError):
    """Validation error."""

    def __init__(self, message: str, code: str = ErrorCode.VALIDATION_ERROR, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, 422, details)


class BadRequestError(APIError):
    """Bad request error."""

    def __init__(self, message: str, code: str = ErrorCode.BAD_REQUEST, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, 400, details)


class ProjectError(APIError):
    """Project-related error."""

    def __init__(self, message: str, code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, 400, details)


class DatasetError(APIError):
    """Dataset-related error."""

    def __init__(self, message: str, code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code, 400, details)