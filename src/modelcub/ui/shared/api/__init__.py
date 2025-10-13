"""Shared API module - configuration, schemas, and errors."""
from .config import APIConfig, Endpoints
from .schemas import (
    APIResponse,
    ErrorDetail,
    ResponseMeta,
    Project,
    ProjectConfig,
    ProjectInfo,
    ProjectPaths,
    ProjectConfigFull,
    CreateProjectRequest,
    SetConfigRequest,
    DeleteProjectRequest,
    Dataset,
    DatasetDetail,
    ImportDatasetRequest,
    ImageInfo,
    Model,
    TrainingRun,
)
from .errors import (
    ErrorCode,
    APIError,
    NotFoundError,
    ValidationError,
    BadRequestError,
    ProjectError,
    DatasetError,
)

__all__ = [
    # Config
    "APIConfig",
    "Endpoints",
    # Schemas
    "APIResponse",
    "ErrorDetail",
    "ResponseMeta",
    "Project",
    "ProjectConfig",
    "ProjectInfo",
    "ProjectPaths",
    "ProjectConfigFull",
    "CreateProjectRequest",
    "SetConfigRequest",
    "DeleteProjectRequest",
    "Dataset",
    "DatasetDetail",
    "ImportDatasetRequest",
    "ImageInfo",
    "Model",
    "TrainingRun",
    # Errors
    "ErrorCode",
    "APIError",
    "NotFoundError",
    "ValidationError",
    "BadRequestError",
    "ProjectError",
    "DatasetError",
]