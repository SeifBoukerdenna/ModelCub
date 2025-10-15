"""Dataset management API routes."""
from typing import List, Optional
import logging

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse

from .datasets_operations import DatasetOperations
from ..dependencies import ProjectRequired
from ...shared.api.config import Endpoints
from ...shared.api.schemas import (
    APIResponse,
    Dataset as DatasetSchema,
    DatasetDetail as DatasetDetailSchema,
    ImportDatasetRequest,
    ImageInfo,
)
from ...shared.api.errors import NotFoundError, DatasetError, ErrorCode

logger = logging.getLogger(__name__)
router = APIRouter(prefix=Endpoints.DATASETS, tags=["Datasets"])


@router.get("")
async def list_datasets(project: ProjectRequired) -> APIResponse[List[DatasetSchema]]:
    """List all datasets in project."""
    try:
        logger.info(f"Listing datasets for project: {project.name}")
        datasets = DatasetOperations.list_datasets(project)
        return APIResponse(
            success=True,
            data=datasets,
            message=f"Found {len(datasets)} dataset(s)"
        )
    except Exception as e:
        logger.error(f"Failed to list datasets: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to list datasets: {str(e)}",
            code=ErrorCode.DATASET_INVALID,
            details={"error": str(e)}
        )


@router.get("/{dataset_name}")
async def get_dataset(
    dataset_name: str,
    project: ProjectRequired,
    include_images: bool = False,
    split: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> APIResponse[DatasetDetailSchema]:
    """Get dataset details with optional images."""
    try:
        logger.info(f"Getting dataset: {dataset_name}, include_images={include_images}")
        dataset_schema = DatasetOperations.get_dataset_detail(
            project,
            dataset_name,
            include_images=include_images,
            split=split,
            limit=limit,
            offset=offset
        )
        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Dataset '{dataset_name}' loaded successfully"
        )
    except ValueError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.DATASET_NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to get dataset: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to load dataset: {str(e)}",
            code=ErrorCode.DATASET_INVALID
        )


@router.post("/import")
async def import_dataset(
    request: ImportDatasetRequest,
    project: ProjectRequired
) -> APIResponse[DatasetSchema]:
    """Import dataset from source path."""
    try:
        logger.info(f"Importing dataset from: {request.source}")
        dataset_schema = DatasetOperations.import_from_path(
            project,
            request.source,
            request.name,
            request.classes,
            request.recursive,
            request.copy_files
        )
        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Dataset imported successfully: {dataset_schema.name}"
        )
    except ValueError as e:
        raise DatasetError(message=str(e), code=ErrorCode.DATASET_IMPORT_FAILED)
    except Exception as e:
        logger.error(f"Failed to import dataset: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to import dataset: {str(e)}",
            code=ErrorCode.DATASET_IMPORT_FAILED
        )


@router.post("/import-files")
async def import_dataset_files(
    files: List[UploadFile] = File(...),
    name: Optional[str] = Form(None),
    classes: Optional[str] = Form(None),
    recursive: bool = Form(True),
    project: ProjectRequired = None
) -> APIResponse[DatasetSchema]:
    """Import dataset from uploaded files."""
    try:
        logger.info(f"Importing {len(files)} files")
        dataset_schema = DatasetOperations.import_from_files(
            project, files, name, classes, recursive
        )
        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Imported {dataset_schema.images} image(s) into dataset '{dataset_schema.name}'"
        )
    except ValueError as e:
        raise DatasetError(message=str(e), code=ErrorCode.DATASET_IMPORT_FAILED)
    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to import files: {str(e)}",
            code=ErrorCode.FILE_UPLOAD_FAILED
        )


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    project: ProjectRequired = None
) -> APIResponse[DatasetSchema]:
    """Upload dataset archive (zip/tar)."""
    try:
        logger.info(f"Uploading dataset: {file.filename}")
        dataset_schema = DatasetOperations.import_from_archive(project, file, dataset_name)
        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Dataset uploaded successfully: {dataset_schema.name}"
        )
    except ValueError as e:
        raise DatasetError(message=str(e), code=ErrorCode.DATASET_INVALID)
    except Exception as e:
        logger.error(f"Failed to upload dataset: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to upload dataset: {str(e)}",
            code=ErrorCode.DATASET_IMPORT_FAILED
        )

@router.get("/{dataset_name}/image/{image_path:path}")
async def get_image(
    dataset_name: str,
    image_path: str,
    project_path: str
) -> FileResponse:
    """Serve an image file."""
    from modelcub.sdk import Project

    project = Project(project_path)
    dataset = project.get_dataset(dataset_name)
    file_path = dataset.path / image_path

    if not file_path.exists() or not file_path.is_file():
        raise NotFoundError(message="Image not found", code=ErrorCode.FILE_NOT_FOUND)

    return FileResponse(file_path)

@router.get("/{dataset_name}/images")
async def list_dataset_images(
    dataset_name: str,
    project: ProjectRequired,
    split: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> APIResponse[List[ImageInfo]]:
    """List images in dataset."""
    try:
        logger.info(f"Listing images for dataset: {dataset_name}, split: {split}")
        images, total = DatasetOperations.list_images(project, dataset_name, split, limit, offset)
        return APIResponse(
            success=True,
            data=images,
            message=f"Found {total} image(s), showing {len(images)}"
        )
    except ValueError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.DATASET_NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to list images: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to list images: {str(e)}",
            code=ErrorCode.DATASET_INVALID
        )


@router.post("/{dataset_id}/classes")
async def add_class(
    dataset_id: str,
    class_name: str = Form(...),
    project: ProjectRequired = None
) -> APIResponse[List[str]]:
    """Add a class to dataset."""
    try:
        logger.info(f"Adding class '{class_name}' to dataset: {dataset_id}")
        classes = DatasetOperations.add_class(project, dataset_id, class_name)
        return APIResponse(
            success=True,
            data=classes,
            message=f"Class '{class_name}' added successfully"
        )
    except ValueError as e:
        raise DatasetError(message=str(e), code=ErrorCode.DATASET_INVALID)
    except Exception as e:
        logger.error(f"Failed to add class: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to add class: {str(e)}",
            code=ErrorCode.DATASET_INVALID
        )


@router.delete("/{dataset_id}/classes/{class_name}")
async def remove_class(
    dataset_id: str,
    class_name: str,
    project: ProjectRequired = None
) -> APIResponse[List[str]]:
    """Remove a class from dataset."""
    try:
        logger.info(f"Removing class '{class_name}' from dataset: {dataset_id}")
        classes = DatasetOperations.remove_class(project, dataset_id, class_name)
        return APIResponse(
            success=True,
            data=classes,
            message=f"Class '{class_name}' removed successfully"
        )
    except ValueError as e:
        raise DatasetError(message=str(e), code=ErrorCode.DATASET_INVALID)
    except Exception as e:
        logger.error(f"Failed to remove class: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to remove class: {str(e)}",
            code=ErrorCode.DATASET_INVALID
        )


@router.put("/{dataset_id}/classes/{old_name}")
async def rename_class(
    dataset_id: str,
    old_name: str,
    new_name: str = Form(...),
    project: ProjectRequired = None
) -> APIResponse[List[str]]:
    """Rename a class in dataset."""
    try:
        logger.info(f"Renaming class '{old_name}' to '{new_name}' in dataset: {dataset_id}")
        classes = DatasetOperations.rename_class(project, dataset_id, old_name, new_name)
        return APIResponse(
            success=True,
            data=classes,
            message=f"Class renamed: '{old_name}' → '{new_name}'"
        )
    except ValueError as e:
        raise DatasetError(message=str(e), code=ErrorCode.DATASET_INVALID)
    except Exception as e:
        logger.error(f"Failed to rename class: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to rename class: {str(e)}",
            code=ErrorCode.DATASET_INVALID
        )


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    project: ProjectRequired = None
) -> APIResponse[None]:
    """Delete a dataset."""
    try:
        logger.info(f"Deleting dataset: {dataset_id}")
        DatasetOperations.delete_dataset(project, dataset_id)
        return APIResponse(
            success=True,
            data=None,
            message=f"Dataset '{dataset_id}' deleted successfully"
        )
    except ValueError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.DATASET_NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to delete dataset: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to delete dataset: {str(e)}",
            code=ErrorCode.DATASET_INVALID
        )