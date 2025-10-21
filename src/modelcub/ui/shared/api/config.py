"""Shared API configuration and endpoints."""
from typing import Final


class APIConfig:
    """API configuration constants."""
    VERSION: Final[str] = "v1"
    PREFIX: Final[str] = f"/api/{VERSION}"
    TIMEOUT: Final[int] = 30000


class Endpoints:
    """Centralized endpoint definitions."""

    # Health
    HEALTH = "/health"

    # Projects
    PROJECTS = "/projects"
    PROJECT_BY_PATH = "/projects/by-path"
    PROJECT_CONFIG = "/projects/config"
    PROJECT_DELETE = "/projects/delete"

    # Datasets
    DATASETS = "/datasets"
    DATASET_DETAIL = "/datasets/{dataset_id}"
    DATASET_IMPORT = "/datasets/import"
    DATASET_UPLOAD = "/datasets/upload"
    DATASET_IMAGES = "/datasets/{dataset_id}/images"
    DATASET_IMAGE = "/datasets/{dataset_id}/image/{image_path}"  # ADD THIS

    # Annotations (ADD THESE)
    ANNOTATIONS = "/datasets/{dataset_id}/annotations"
    ANNOTATION_DETAIL = "/datasets/{dataset_id}/annotations/{image_id}"
    ANNOTATION_DELETE_BOX = "/datasets/{dataset_id}/annotations/{image_id}/boxes/{box_index}"

    # Models
    MODELS = "/models"
    MODEL_DETAIL = "/models/{model_id}"

    # Jobs
    JOBS = "/jobs"
    JOB_DETAIL = "/jobs/{job_id}"
    JOB_START = "/jobs/{job_id}/start"
    JOB_PAUSE = "/jobs/{job_id}/pause"
    JOB_CANCEL = "/jobs/{job_id}/cancel"
    JOB_TASKS = "/jobs/{job_id}/tasks"
    JOB_NEXT_TASK = "/jobs/{job_id}/next-task"

    # WebSocket
    WS = "/ws"

    @staticmethod
    def format(endpoint: str, **kwargs) -> str:
        """Format endpoint with path parameters."""
        return endpoint.format(**kwargs)