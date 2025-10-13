"""Shared API schemas (Pydantic models)."""
from typing import TypeVar, Generic, Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


# Generic type for data
T = TypeVar('T')


class ResponseMeta(BaseModel):
    """Response metadata."""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    request_id: Optional[str] = None


class ErrorDetail(BaseModel):
    """Standardized error detail."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class APIResponse(BaseModel, Generic[T]):
    """Standardized API response wrapper."""
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None
    message: Optional[str] = None
    meta: Optional[ResponseMeta] = None


# ==================== PROJECT SCHEMAS ====================

class ProjectConfig(BaseModel):
    """Project configuration."""
    device: str
    batch_size: int
    image_size: int
    workers: int
    format: str


class ProjectInfo(BaseModel):
    """Project information."""
    name: str
    created: str
    version: str


class ProjectPaths(BaseModel):
    """Project paths configuration."""
    data: str
    runs: str
    reports: str


class ProjectConfigFull(BaseModel):
    """Complete project configuration."""
    project: ProjectInfo
    defaults: ProjectConfig
    paths: ProjectPaths


class Project(BaseModel):
    """Project model."""
    name: str
    path: str
    created: str
    version: str
    config: ProjectConfig
    is_current: bool = False


class CreateProjectRequest(BaseModel):
    """Request to create a project."""
    name: str = Field(..., min_length=1, max_length=100)
    path: Optional[str] = None
    force: bool = False


class SetConfigRequest(BaseModel):
    """Request to set config value."""
    key: str
    value: Any  # Can be str, int, bool, float


class DeleteProjectRequest(BaseModel):
    """Request to delete a project."""
    confirm: bool = False


# ==================== DATASET SCHEMAS ====================

class Dataset(BaseModel):
    """Dataset model."""
    name: str
    id: str
    status: str
    images: int
    classes: List[str]
    path: str
    created: Optional[str] = None
    source: Optional[str] = None
    size_bytes: int = 0
    size_formatted: str = "0 B"


class DatasetDetail(Dataset):
    """Detailed dataset information."""
    train_images: int = 0
    valid_images: int = 0
    unlabeled_images: int = 0


class ImportDatasetRequest(BaseModel):
    """Request to import dataset."""
    source: str
    name: Optional[str] = None
    recursive: bool = False
    copy_files: bool = False
    classes: Optional[List[str]] = [],


class ImageInfo(BaseModel):
    """Image information."""
    filename: str
    path: str
    width: int
    height: int
    size_bytes: int
    has_labels: bool
    split: str  # train, val, test


# ==================== MODEL SCHEMAS ====================

class Model(BaseModel):
    """Model information."""
    id: str
    name: str
    type: str
    created: str
    path: Optional[str] = None


class TrainingRun(BaseModel):
    """Training run information."""
    id: str
    model_id: str
    dataset_id: str
    status: str
    created: str
    metrics: Optional[Dict[str, float]] = None