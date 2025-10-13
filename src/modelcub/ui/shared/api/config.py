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

    # Models
    MODELS = "/models"
    MODEL_DETAIL = "/models/{model_id}"

    # WebSocket
    WS = "/ws"

    @staticmethod
    def format(endpoint: str, **kwargs) -> str:
        """Format endpoint with path parameters."""
        return endpoint.format(**kwargs)