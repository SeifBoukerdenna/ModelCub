"""API schemas with guaranteed meta field."""
from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar, List, Dict, Any
from datetime import datetime

T = TypeVar('T')

class ResponseMeta(BaseModel):
    """Response metadata - never None."""
    request_id: Optional[str] = None
    duration_ms: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

    class Config:
        extra = "allow"

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class APIResponse(BaseModel, Generic[T]):
    """Standard API response."""
    success: bool
    data: Optional[T] = None
    message: str = ""
    error: Optional[ErrorDetail] = None
    meta: ResponseMeta = Field(default_factory=ResponseMeta)  # CRITICAL: Always present

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

# Project schemas
class ProjectConfig(BaseModel):
    device: str
    batch_size: int
    image_size: int
    workers: int
    format: str

class Project(BaseModel):
    name: str
    path: str
    created: str
    version: str
    config: ProjectConfig
    is_current: bool = False

class ProjectInfo(BaseModel):
    name: str
    created: str
    version: str

class ProjectPaths(BaseModel):
    data: str
    runs: str
    reports: str

class ProjectConfigFull(BaseModel):
    project: ProjectInfo
    defaults: ProjectConfig
    paths: ProjectPaths

class CreateProjectRequest(BaseModel):
    name: str
    path: Optional[str] = None
    force: bool = False

class SetConfigRequest(BaseModel):
    key: str
    value: Any

class DeleteProjectRequest(BaseModel):
    path: str
    confirm: bool = False

class Dataset(BaseModel):
    name: str
    path: str
    status: str
    classes: List[str]
    images: int
    created: Optional[str] = None

class ImageInfo(BaseModel):
    id: str
    filename: str
    path: str
    split: str
    width: Optional[int] = None
    height: Optional[int] = None
    labeled: bool = False
    num_boxes: int = 0

class DatasetDetail(Dataset):
    train_images: int = 0
    valid_images: int = 0
    unlabeled_images: int = 0
    total_images: int = 0
    image_list: Optional[List[ImageInfo]] = None

class DatasetImages(BaseModel):
    """Dataset images response."""
    images: List[ImageInfo]
    total: int
    split: Optional[str] = None

class ImportDatasetRequest(BaseModel):
    source: str
    name: Optional[str] = None
    classes: Optional[List[str]] = None
    recursive: bool = True
    copy_files: bool = True

class Model(BaseModel):
    id: str
    name: str
    task: str
    created: str
    status: str

class TrainingRun(BaseModel):
    id: str
    name: str
    dataset: str
    model: str
    status: str
    created: str

