"""Dataset management API routes."""
from typing import Optional, List, Union, Dict, Any
from pathlib import Path
import logging
import os

from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, Field

from modelcub.sdk import Dataset
from modelcub.sdk.project import Project

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/datasets")

# Get working directory
WORKING_DIR = Path(os.environ.get("MODELCUB_WORKING_DIR", Path.cwd()))


# Request/Response Models
class ImportDatasetRequest(BaseModel):
    """Request model for importing a dataset."""
    source: str = Field(..., description="Path to source directory")
    name: Optional[str] = Field(None, description="Dataset name (auto-generated if None)")
    recursive: bool = Field(False, description="Scan subdirectories")
    copy: bool = Field(True, description="Copy files (True) or create symlinks (False)")


class DatasetResponse(BaseModel):
    """Dataset response model."""
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


class DatasetDetailResponse(DatasetResponse):
    """Detailed dataset response with split information."""
    train_images: int = 0
    valid_images: int = 0
    unlabeled_images: int = 0


class ApiResponse(BaseModel):
    """Standard API response."""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


# Helper Functions
def _get_project_from_path(project_path: Optional[str] = None) -> Project:
    """Get project from path or current working directory."""
    try:
        target_path = Path(project_path) if project_path else WORKING_DIR
        logger.info(f"Loading project from {'provided path' if project_path else 'WORKING_DIR'}: {target_path}")

        if not (target_path / ".modelcub").exists():
            logger.warning(f"No .modelcub folder found at: {target_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No project found at {target_path}. Please create or select a project first."
            )

        project = Project.load(str(target_path))
        logger.info(f"Successfully loaded project: {project.name} from {target_path}")
        return project

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load project: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load project: {str(e)}"
        )


def _dataset_to_response(dataset: Union[Dataset, Dict[str, Any]]) -> DatasetResponse:
    """Convert Dataset object or dict to response model."""
    # Handle dict from list_datasets()
    if isinstance(dataset, dict):
        return DatasetResponse(
            name=dataset.get("name", ""),
            id=dataset.get("id", ""),
            status=dataset.get("status", "unknown"),
            images=dataset.get("images", 0),
            classes=dataset.get("classes", []),
            path=dataset.get("path", ""),
            created=dataset.get("created"),
            source=dataset.get("source"),
            size_bytes=dataset.get("size_bytes", 0),
            size_formatted=dataset.get("size_formatted", "0 B")
        )

    # Handle Dataset object
    info = dataset.info()
    return DatasetResponse(
        name=dataset.name,
        id=dataset.id,
        status=dataset.status,
        images=dataset.images,
        classes=dataset.classes,
        path=str(dataset.path),
        created=dataset.created,
        source=dataset.source,
        size_bytes=info.size_bytes,
        size_formatted=info.size
    )


def _dataset_to_detail_response(dataset: Dataset) -> DatasetDetailResponse:
    """Convert Dataset to detailed response model."""
    info = dataset.info()
    return DatasetDetailResponse(
        name=dataset.name,
        id=dataset.id,
        status=dataset.status,
        images=info.total_images,
        classes=dataset.classes,
        path=str(dataset.path),
        created=dataset.created,
        source=dataset.source,
        size_bytes=info.size_bytes,
        size_formatted=info.size,
        train_images=info.train_images,
        valid_images=info.valid_images,
        unlabeled_images=info.unlabeled_images
    )


# Routes
@router.get("/")
async def list_datasets(x_project_path: Optional[str] = Header(None)):
    """List all datasets in specified project."""
    try:
        project = _get_project_from_path(x_project_path)
        logger.info(f"Listing datasets for project: {project.name}")

        datasets = project.datasets.list_datasets()
        logger.info(f"Found {len(datasets)} datasets")

        return {
            "success": True,
            "datasets": [_dataset_to_response(ds) for ds in datasets],
            "count": len(datasets),
            "message": f"Found {len(datasets)} dataset(s) in project '{project.name}'"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list datasets: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list datasets: {str(e)}"
        )


@router.get("/{name}")
async def get_dataset(name: str, x_project_path: Optional[str] = Header(None)):
    """Get detailed information about a specific dataset."""
    try:
        project = _get_project_from_path(x_project_path)
        logger.info(f"Getting dataset '{name}' from project: {project.name}")

        if not Dataset.exists(name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{name}' not found in project '{project.name}'"
            )

        dataset = Dataset.load(name)

        return {
            "success": True,
            "dataset": _dataset_to_detail_response(dataset)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dataset '{name}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dataset: {str(e)}"
        )


@router.post("/import")
async def import_dataset(
    request: ImportDatasetRequest,
    x_project_path: Optional[str] = Header(None)
):
    """Import images from a directory into the current project."""
    try:
        project = _get_project_from_path(x_project_path)
        logger.info(f"Importing dataset into project: {project.name}")

        source_path = Path(request.source)
        if not source_path.is_absolute():
            source_path = WORKING_DIR / source_path

        if not source_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source directory not found: {source_path}"
            )

        if not source_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source is not a directory: {source_path}"
            )

        logger.info(f"Importing from: {source_path}")

        dataset = project.datasets.from_images(
            source=str(source_path),
            name=request.name,
            recursive=request.recursive,
            copy=request.copy
        )

        logger.info(f"Successfully imported dataset: {dataset.name} ({dataset.images} images)")

        return {
            "success": True,
            "message": f"Successfully imported {dataset.images} images into dataset '{dataset.name}'",
            "dataset": _dataset_to_response(dataset)
        }

    except HTTPException:
        raise
    except RuntimeError as e:
        logger.warning(f"Dataset import validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to import dataset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import dataset: {str(e)}"
        )


@router.delete("/{name}")
async def delete_dataset(
    name: str,
    confirm: bool = False,
    x_project_path: Optional[str] = Header(None)
):
    """Delete a dataset from the current project."""
    try:
        project = _get_project_from_path(x_project_path)
        logger.info(f"Deleting dataset '{name}' from project: {project.name}")

        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must confirm deletion by setting confirm=true"
            )

        if not Dataset.exists(name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset '{name}' not found in project '{project.name}'"
            )

        dataset = Dataset.load(name)
        dataset.delete(confirm=True)

        logger.info(f"Successfully deleted dataset: {name}")

        return {
            "success": True,
            "message": f"Successfully deleted dataset '{name}'"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete dataset '{name}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete dataset: {str(e)}"
        )