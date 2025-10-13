"""
Dataset management API routes - SDK-only implementation.

All operations go through the SDK as the single source of truth.
"""
from typing import List, Optional
from pathlib import Path
import logging
import tempfile
import shutil

from fastapi import APIRouter, UploadFile, File, Form

from modelcub.sdk import Project

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


def _dataset_to_schema(dataset, project_path: str) -> DatasetSchema:
    """Convert SDK Dataset to API schema."""
    info = dataset.info()
    size_bytes, size_formatted = _calculate_directory_size(info.path)

    return DatasetSchema(
        name=info.name,
        id=info.id,
        status=info.status,
        images=info.images,
        classes=info.classes,
        path=str(info.path),
        created=info.created,
        source=info.source,
        size_bytes=size_bytes,
        size_formatted=size_formatted
    )


@router.get("")
async def list_datasets(project: ProjectRequired) -> APIResponse[List[DatasetSchema]]:
    """
    List all datasets in project.

    Uses SDK: project.list_datasets()
    """
    try:
        logger.info(f"Listing datasets for project: {project.name}")

        # Use SDK to list datasets
        datasets = project.list_datasets()

        dataset_schemas = [
            _dataset_to_schema(ds, project.path)
            for ds in datasets
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
    """
    Get dataset details.

    Uses SDK: project.get_dataset()
    """
    try:
        logger.info(f"Getting dataset: {dataset_id}")

        # Use SDK to get dataset
        dataset = project.get_dataset(dataset_id)
        info = dataset.info()

        # Get split counts using SDK
        split_counts = dataset.get_split_counts()

        base_schema = _dataset_to_schema(dataset, project.path)

        dataset_schema = DatasetDetailSchema(
            **base_schema.model_dump(),
            train_images=split_counts.get("train", 0),
            valid_images=split_counts.get("val", 0),
            unlabeled_images=split_counts.get("unlabeled", 0)
        )

        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Dataset '{dataset_id}' loaded successfully"
        )

    except ValueError as e:
        raise NotFoundError(
            message=str(e),
            code=ErrorCode.DATASET_NOT_FOUND
        )
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
    """
    Import dataset from source path.

    Uses SDK: project.import_dataset()
    """
    try:
        logger.info(f"Importing dataset from: {request.source}")
        logger.info(f"Classes: {request.classes}")

        # Use SDK to import dataset
        dataset = project.import_dataset(
            source=request.source,
            name=request.name,
            classes=request.classes,
            recursive=request.recursive,
            copy=request.copy_files,
            validate=True,
            force=False
        )

        dataset_schema = _dataset_to_schema(dataset, project.path)

        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Dataset imported successfully: {dataset.name}"
        )

    except ValueError as e:
        raise DatasetError(
            message=str(e),
            code=ErrorCode.DATASET_IMPORT_FAILED
        )
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
    """
    Import dataset from uploaded files.

    Uses SDK: project.import_dataset()
    """
    temp_dir = None

    try:
        logger.info(f"Importing {len(files)} files")
        logger.info(f"Classes string: {classes}")

        # Create temp directory for uploaded files
        temp_dir = Path(tempfile.mkdtemp(prefix="modelcub_upload_"))

        # Save uploaded files
        for file in files:
            if not file.filename:
                continue

            # Handle webkitRelativePath or regular filename
            filename = Path(file.filename).name
            if not filename:
                continue

            file_path = temp_dir / filename
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

        logger.info(f"Saved {len(files)} files to {temp_dir}")

        # Parse classes
        classes_list = None
        if classes:
            classes_list = [c.strip() for c in classes.split(",") if c.strip()]
            logger.info(f"Parsed classes: {classes_list}")

        # Use SDK to import dataset
        dataset = project.import_dataset(
            source=str(temp_dir),
            name=name,
            classes=classes_list,
            recursive=recursive,
            copy=True,
            validate=True,
            force=False
        )

        dataset_schema = _dataset_to_schema(dataset, project.path)

        logger.info(f"Import successful: {dataset.name} with {dataset_schema.images} images")

        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Imported {dataset_schema.images} image(s) into dataset '{dataset.name}'"
        )

    except ValueError as e:
        raise DatasetError(
            message=str(e),
            code=ErrorCode.DATASET_IMPORT_FAILED
        )
    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to import files: {str(e)}",
            code=ErrorCode.FILE_UPLOAD_FAILED
        )
    finally:
        # Clean up temporary directory
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp dir: {e}")


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_name: Optional[str] = Form(None),
    project: ProjectRequired = None
) -> APIResponse[DatasetSchema]:
    """
    Upload dataset archive (zip/tar).

    Uses SDK: project.import_dataset() after extracting archive.
    """
    temp_dir = None

    try:
        logger.info(f"Uploading dataset: {file.filename}")

        if not file.filename or not file.filename.endswith(('.zip', '.tar.gz', '.tar')):
            raise DatasetError(
                message="Invalid file type. Only .zip, .tar.gz, and .tar files are supported.",
                code=ErrorCode.DATASET_INVALID
            )

        # Create temporary directory for extraction
        temp_dir = Path(tempfile.mkdtemp(prefix="modelcub_upload_"))

        # Save uploaded file
        archive_path = temp_dir / file.filename
        with open(archive_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)

        # Extract archive
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()

        if file.filename.endswith('.zip'):
            import zipfile
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        elif file.filename.endswith(('.tar.gz', '.tar')):
            import tarfile
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_dir)

        # Find the actual data directory (handle nested structures)
        data_dir = extract_dir
        contents = list(extract_dir.iterdir())
        if len(contents) == 1 and contents[0].is_dir():
            data_dir = contents[0]

        # Generate dataset name if not provided
        if not dataset_name:
            dataset_name = Path(file.filename).stem.replace('.tar', '')

        # Use SDK to import the extracted dataset
        dataset = project.import_dataset(
            source=str(data_dir),
            name=dataset_name,
            recursive=True,
            copy=True,
            validate=True,
            force=False
        )

        dataset_schema = _dataset_to_schema(dataset, project.path)

        return APIResponse(
            success=True,
            data=dataset_schema,
            message=f"Dataset uploaded successfully: {dataset.name}"
        )

    except DatasetError:
        raise
    except Exception as e:
        logger.error(f"Failed to upload dataset: {e}", exc_info=True)
        raise DatasetError(
            message=f"Failed to upload dataset: {str(e)}",
            code=ErrorCode.DATASET_IMPORT_FAILED
        )
    finally:
        # Clean up temporary directory
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory: {e}")


@router.get("/{dataset_id}/images")
async def list_dataset_images(
    dataset_id: str,
    project: ProjectRequired,
    split: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> APIResponse[List[ImageInfo]]:
    """
    List images in dataset.

    Uses SDK: project.get_dataset() and filesystem access.
    """
    try:
        logger.info(f"Listing images for dataset: {dataset_id}, split: {split}")

        # Use SDK to get dataset
        dataset = project.get_dataset(dataset_id)
        dataset_path = dataset.path

        # Determine which directories to scan
        if split:
            image_dirs = [dataset_path / "images" / split]
        else:
            image_dirs = [
                dataset_path / "images" / s
                for s in ["train", "val", "test", "unlabeled"]
            ]

        # Collect all image files
        images = []
        for img_dir in image_dirs:
            if not img_dir.exists():
                continue

            split_name = img_dir.name
            for img_file in img_dir.glob("*.*"):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                    # Check for corresponding label
                    label_dir = dataset_path / "labels" / split_name
                    label_file = label_dir / f"{img_file.stem}.txt"

                    images.append(ImageInfo(
                        name=img_file.name,
                        path=str(img_file.relative_to(dataset_path)),
                        split=split_name,
                        size=img_file.stat().st_size,
                        has_label=label_file.exists()
                    ))

        # Apply pagination
        total = len(images)
        images = images[offset:offset + limit]

        return APIResponse(
            success=True,
            data=images,
            message=f"Found {total} image(s), showing {len(images)}"
        )

    except ValueError as e:
        raise NotFoundError(
            message=str(e),
            code=ErrorCode.DATASET_NOT_FOUND
        )
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
    """
    Add a class to dataset.

    Uses SDK: dataset.add_class()
    """
    try:
        logger.info(f"Adding class '{class_name}' to dataset: {dataset_id}")

        dataset = project.get_dataset(dataset_id)
        dataset.add_class(class_name)

        # Return updated class list
        classes = dataset.list_classes()

        return APIResponse(
            success=True,
            data=classes,
            message=f"Class '{class_name}' added successfully"
        )

    except ValueError as e:
        raise DatasetError(
            message=str(e),
            code=ErrorCode.DATASET_INVALID
        )
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
    """
    Remove a class from dataset.

    Uses SDK: dataset.remove_class()
    """
    try:
        logger.info(f"Removing class '{class_name}' from dataset: {dataset_id}")

        dataset = project.get_dataset(dataset_id)
        dataset.remove_class(class_name)

        # Return updated class list
        classes = dataset.list_classes()

        return APIResponse(
            success=True,
            data=classes,
            message=f"Class '{class_name}' removed successfully"
        )

    except ValueError as e:
        raise DatasetError(
            message=str(e),
            code=ErrorCode.DATASET_INVALID
        )
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
    """
    Rename a class in dataset.

    Uses SDK: dataset.rename_class()
    """
    try:
        logger.info(f"Renaming class '{old_name}' to '{new_name}' in dataset: {dataset_id}")

        dataset = project.get_dataset(dataset_id)
        dataset.rename_class(old_name, new_name)

        # Return updated class list
        classes = dataset.list_classes()

        return APIResponse(
            success=True,
            data=classes,
            message=f"Class renamed: '{old_name}' → '{new_name}'"
        )

    except ValueError as e:
        raise DatasetError(
            message=str(e),
            code=ErrorCode.DATASET_INVALID
        )
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
    """Delete a dataset. Uses SDK: dataset.delete()"""
    try:
        logger.info(f"Deleting dataset: {dataset_id}")
        dataset = project.get_dataset(dataset_id)
        dataset.delete(confirm=True)

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