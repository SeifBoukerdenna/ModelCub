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
            return total_size, f"{size_display:.1f} {unit}"  # Return original int
        size_display /= 1024
    return total_size, f"{size_display:.1f} TB"


def _registry_dict_to_schema(ds_dict: dict, project_path: str) -> DatasetSchema:
    """Convert registry dict to API schema."""
    dataset_name = ds_dict.get("name", ds_dict.get("dataset", "unknown"))
    dataset_path = Path(project_path) / "data" / "datasets" / dataset_name
    size_bytes, size_formatted = _calculate_directory_size(dataset_path)

    return DatasetSchema(
        name=dataset_name,
        id=ds_dict.get("id", dataset_name),
        status="ready",
        images=ds_dict.get("num_images", 0),
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

        # CORRECT: project.datasets is the DatasetRegistry
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

        # Use service layer for import
        from modelcub.services.image_service import import_images, ImportImagesRequest

        import_request = ImportImagesRequest(
            project_path=project.path,
            source=request.source,
            dataset_name=request.name,
            recursive=request.recursive,
            copy=request.copy_files
        )

        result = import_images(import_request)

        if not result.success:
            raise DatasetError(
                message=result.message or "Failed to import dataset",
                code=ErrorCode.DATASET_IMPORT_FAILED
            )

        dataset_name = request.name or Path(request.source).name
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

        ds_name = dataset_name or Path(file.filename).stem
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
    recursive: bool = Form(True),
    project: ProjectRequired = None
) -> APIResponse[DatasetSchema]:
    """Import dataset from uploaded files."""
    temp_dir = None

    try:
        logger.info(f"Importing {len(files)} files")

        temp_dir = Path(tempfile.mkdtemp())

        # Save files
        for file in files:
            if not file.filename:
                continue
            filename = Path(file.filename).name
            if not filename:
                continue
            file_path = temp_dir / filename
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

        logger.info(f"Saved files to {temp_dir}")

        # Import using SDK
        from modelcub.sdk.dataset import Dataset
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(project.path)
            dataset = Dataset.from_images(
                source=temp_dir,
                name=name,
                recursive=False,
                copy=True,
                validate=True
            )
            dataset_name = dataset.name
        finally:
            os.chdir(original_cwd)

        # Count actual images
        dataset_dir = Path(project.path) / "data" / "datasets" / dataset_name
        images_dir = dataset_dir / "images" / "unlabeled"

        if images_dir.exists():
            image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.png")) + list(images_dir.glob("*.bmp"))
            image_count = len(image_files)

            # Update registry
            ds_dict = project.datasets.get_dataset(dataset_name)
            if ds_dict:
                ds_dict["num_images"] = image_count
                if "images" not in ds_dict:
                    ds_dict["images"] = {}
                ds_dict["images"]["total"] = image_count
                ds_dict["images"]["unlabeled"] = image_count
                project.datasets.add_dataset(ds_dict)

        # Get updated data
        ds_dict = project.datasets.get_dataset(dataset_name)
        if not ds_dict:
            raise DatasetError("Dataset not in registry", ErrorCode.DATASET_INVALID)

        dataset_schema = _registry_dict_to_schema(ds_dict, project.path)
        return APIResponse(success=True, data=dataset_schema, message=f"Imported {len(files)} files")

    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        raise DatasetError(f"Failed: {str(e)}", ErrorCode.FILE_UPLOAD_FAILED)
    finally:
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)