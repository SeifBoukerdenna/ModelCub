"""Dataset management API routes - Fixed."""
from typing import List, Optional
from pathlib import Path
import logging
import tempfile
import shutil

from fastapi import APIRouter, UploadFile, File, Form

from ..dependencies import ProjectRequired
from ...shared.api.config import Endpoints
from ...shared.api.schemas import (
    APIResponse,
    Dataset as DatasetSchema,
    DatasetDetail as DatasetDetailSchema,
    ImportDatasetRequest,
)
from ...shared.api.errors import NotFoundError, DatasetError, ErrorCode

logger = logging.getLogger(__name__)
router = APIRouter(prefix=Endpoints.DATASETS, tags=["Datasets"])


def _calculate_directory_size(path: Path) -> tuple[int, str]:
    """Calculate total size of directory."""
    total_size = 0
    try:
        for item in path.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
    except Exception as e:
        logger.warning(f"Failed to calculate size for {path}: {e}")

    # Format size string
    size_display = total_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_display < 1024:
            return total_size, f"{size_display:.1f} {unit}"
        size_display /= 1024
    return total_size, f"{size_display:.1f} TB"


def _registry_dict_to_schema(ds_dict: dict, project_path: str) -> DatasetSchema:
    """Convert registry dict to API schema."""
    dataset_name = ds_dict.get("name", ds_dict.get("dataset", "unknown"))
    dataset_path = Path(project_path) / "data" / "datasets" / dataset_name

    # Get image count from multiple possible locations
    image_count = 0
    if "num_images" in ds_dict:
        image_count = ds_dict["num_images"]
    elif "images" in ds_dict:
        if isinstance(ds_dict["images"], dict):
            image_count = ds_dict["images"].get("total", 0)
        else:
            image_count = ds_dict["images"]

    size_bytes, size_formatted = _calculate_directory_size(dataset_path)

    return DatasetSchema(
        name=dataset_name,
        id=ds_dict.get("id", dataset_name),
        status=ds_dict.get("status", "ready"),
        images=image_count,
        classes=ds_dict.get("classes", []),
        path=str(dataset_path),
        created=ds_dict.get("created"),
        source=ds_dict.get("source"),
        size_bytes=size_bytes,
        size_formatted=size_formatted
    )


@router.get("")
async def list_datasets(project: ProjectRequired) -> APIResponse[List[DatasetSchema]]:
    """List all datasets in project."""
    try:
        logger.info(f"Listing datasets for project: {project.name}")

        datasets_list = project.datasets.list_datasets()

        dataset_schemas = [
            _registry_dict_to_schema(ds_dict, project.path)
            for ds_dict in datasets_list
        ]

        return APIResponse(
            success=True,
            data=dataset_schemas,
            message=f"Found {len(dataset_schemas)} dataset(s)"
        )

    except Exception as e:
        logger.error(f"Failed to list datasets: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to list datasets: {str(e)}",
            code=ErrorCode.DATASET_INVALID,
            details={"error": str(e)}
        )


@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    project: ProjectRequired
) -> APIResponse[DatasetDetailSchema]:
    """Get dataset details."""
    try:
        logger.info(f"Getting dataset: {dataset_id}")

        ds_dict = project.datasets.get_dataset(dataset_id)

        if not ds_dict:
            raise NotFoundError(
                message=f"Dataset not found: {dataset_id}",
                code=ErrorCode.DATASET_NOT_FOUND
            )

        base_schema = _registry_dict_to_schema(ds_dict, project.path)
        dataset_path = Path(project.path) / "data" / "datasets" / dataset_id

        train_count = sum(1 for _ in (dataset_path / "images" / "train").glob("*.*")) if (dataset_path / "images" / "train").exists() else 0
        valid_count = sum(1 for _ in (dataset_path / "images" / "val").glob("*.*")) if (dataset_path / "images" / "val").exists() else 0
        unlabeled_count = sum(1 for _ in (dataset_path / "images" / "unlabeled").glob("*.*")) if (dataset_path / "images" / "unlabeled").exists() else 0

        dataset_schema = DatasetDetailSchema(
            **base_schema.model_dump(),
            train_images=train_count,
            valid_images=valid_count,
            unlabeled_images=unlabeled_count
        )

        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Dataset '{dataset_id}' loaded successfully"
        )

    except NotFoundError:
        raise
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
    """Import dataset from source."""
    try:
        logger.info(f"Importing dataset from: {request.source}")
        logger.info(f"The classes are ${request.classes=}")
        from modelcub.services.image_service import import_images, ImportImagesRequest

        import_request = ImportImagesRequest(
            project_path=project.path,
            source=request.source,
            dataset_name=request.name,
            recursive=request.recursive,
            copy=request.copy_files,
            classes=request.classes
        )

        result = import_images(import_request)

        if not result.success:
            raise DatasetError(
                message=result.message or "Failed to import dataset",
                code=ErrorCode.DATASET_IMPORT_FAILED
            )

        dataset_name = result.dataset_name
        ds_dict = project.datasets.get_dataset(dataset_name)

        if not ds_dict:
            raise DatasetError(
                message="Dataset imported but not found in registry",
                code=ErrorCode.DATASET_INVALID
            )

        dataset_schema = _registry_dict_to_schema(ds_dict, project.path)

        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Dataset imported successfully: {dataset_name}"
        )

    except DatasetError:
        raise
    except Exception as e:
        logger.error(f"Failed to import dataset: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to import dataset: {str(e)}",
            code=ErrorCode.DATASET_IMPORT_FAILED
        )


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    project: ProjectRequired = None
) -> APIResponse[DatasetSchema]:
    """Upload dataset archive."""
    temp_dir = None

    try:
        logger.info(f"Uploading dataset: {file.filename}")

        if not file.filename or not file.filename.endswith(('.zip', '.tar.gz', '.tar')):
            raise DatasetError(
                message="Invalid file type. Only .zip, .tar.gz, and .tar files are supported.",
                code=ErrorCode.INVALID_FILE_TYPE
            )

        temp_dir = Path(tempfile.mkdtemp())
        archive_path = temp_dir / file.filename

        with open(archive_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        from modelcub.services.image_service import import_images, ImportImagesRequest

        import_request = ImportImagesRequest(
            project_path=project.path,
            source=str(archive_path),
            dataset_name=dataset_name,
            recursive=True,
            copy=True
        )

        result = import_images(import_request)

        if not result.success:
            raise DatasetError(
                message=result.message or "Failed to import uploaded dataset",
                code=ErrorCode.DATASET_IMPORT_FAILED
            )

        ds_name = result.dataset_name
        ds_dict = project.datasets.get_dataset(ds_name)

        if not ds_dict:
            raise DatasetError(
                message="Dataset uploaded but not found in registry",
                code=ErrorCode.DATASET_INVALID
            )

        dataset_schema = _registry_dict_to_schema(ds_dict, project.path)

        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Dataset uploaded successfully: {ds_name}"
        )

    except DatasetError:
        raise
    except Exception as e:
        logger.error(f"Failed to upload dataset: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to upload dataset: {str(e)}",
            code=ErrorCode.FILE_UPLOAD_FAILED
        )
    finally:
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp dir: {e}")


@router.post("/import-files")
async def import_dataset_files(
    files: List[UploadFile] = File(...),
    name: Optional[str] = Form(None),
    classes: Optional[List[str]] = Form(None),
    recursive: bool = Form(True),
    project: ProjectRequired = None
) -> APIResponse[DatasetSchema]:
    """Import dataset from uploaded files."""
    temp_dir = None

    try:
        logger.info(f"Importing {len(files)} files")

        temp_dir = Path(tempfile.mkdtemp())

        # Save uploaded files
        for file in files:
            if not file.filename:
                continue
            filename = Path(file.filename).name
            if not filename:
                continue
            file_path = temp_dir / filename
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

        logger.info(f"Saved {len(files)} files to {temp_dir}")

        from modelcub.services.image_service import import_images, ImportImagesRequest

        import_request = ImportImagesRequest(
            project_path=project.path,
            source=temp_dir,
            dataset_name=name,
            recursive=False,  # Files are already flat
            copy=True,
            validate=True,
            classes=classes
        )

        result = import_images(import_request)

        if not result.success:
            raise DatasetError(
                message=result.message or "Failed to import files",
                code=ErrorCode.FILE_UPLOAD_FAILED
            )

        dataset_name = result.dataset_name

        # Get dataset from registry
        ds_dict = project.datasets.get_dataset(dataset_name)
        if not ds_dict:
            raise DatasetError(
                message="Dataset not found in registry after import",
                code=ErrorCode.DATASET_INVALID
            )

        # Convert to schema (uses the image count from registry)
        dataset_schema = _registry_dict_to_schema(ds_dict, project.path)

        logger.info(f"Import successful: {dataset_name} with {dataset_schema.images} images")

        logger.info(f"{classes=}")

        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Imported {dataset_schema.images} image(s) into dataset '{dataset_name}'"
        )

    except DatasetError:
        raise
    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to import files: {str(e)}",
            code=ErrorCode.FILE_UPLOAD_FAILED
        )
    finally:
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp dir: {e}")