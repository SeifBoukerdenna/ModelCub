"""Dataset management API routes."""
from typing import Optional, List, Union, Dict, Any
from pathlib import Path
import logging
import os
import tempfile
import shutil

from fastapi import APIRouter, HTTPException, status, Header, UploadFile, File, Form
from pydantic import BaseModel

from modelcub.sdk import Dataset
from modelcub.sdk.project import Project
from modelcub.services.image_service import import_images, ImportImagesRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/datasets")

WORKING_DIR = Path(os.environ.get("MODELCUB_WORKING_DIR", Path.cwd()))


class DatasetResponse(BaseModel):
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
    train_images: int = 0
    valid_images: int = 0
    unlabeled_images: int = 0


def _get_project_from_path(project_path: Optional[str] = None) -> Project:
    try:
        target_path = Path(project_path) if project_path else WORKING_DIR
        if not (target_path / ".modelcub").exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No project at {target_path}")
        return Project.load(str(target_path))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load project: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def _dataset_to_response(dataset: Union[Dataset, Dict[str, Any]], project_path: str) -> DatasetResponse:
    """Convert Dataset to response with size."""
    if isinstance(dataset, dict):
        size_bytes = 0
        size_formatted = "0 B"

        dataset_rel_path = dataset.get("path", "")
        if dataset_rel_path:
            full_path = Path(project_path) / dataset_rel_path
            if full_path.exists():
                try:
                    size_bytes = sum(f.stat().st_size for f in full_path.rglob('*') if f.is_file())
                    if size_bytes < 1024:
                        size_formatted = f"{size_bytes} B"
                    elif size_bytes < 1024 * 1024:
                        size_formatted = f"{size_bytes / 1024:.1f} KB"
                    elif size_bytes < 1024 * 1024 * 1024:
                        size_formatted = f"{size_bytes / (1024 * 1024):.1f} MB"
                    else:
                        size_formatted = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
                except Exception as e:
                    logger.error(f"Size calc error: {e}")

        return DatasetResponse(
            name=dataset.get("name", ""),
            id=dataset.get("id", ""),
            status=dataset.get("status", "unknown"),
            images=dataset.get("images", 0),
            classes=dataset.get("classes", []),
            path=dataset.get("path", ""),
            created=dataset.get("created"),
            source=dataset.get("source"),
            size_bytes=size_bytes,
            size_formatted=size_formatted
        )

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


def _dataset_to_detail_response(dataset: Dataset, project_path: str) -> DatasetDetailResponse:
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


@router.get("/")
async def list_datasets(x_project_path: Optional[str] = Header(None)):
    try:
        project = _get_project_from_path(x_project_path)
        datasets = project.datasets.list_datasets()

        dataset_responses = []
        for ds in datasets:
            try:
                response = _dataset_to_response(ds, project.path)
                dataset_responses.append(response)
            except Exception as e:
                logger.error(f"Failed to convert dataset: {e}")
                continue

        return {
            "success": True,
            "datasets": dataset_responses,
            "count": len(dataset_responses),
            "message": f"Found {len(dataset_responses)} dataset(s) in project '{project.name}'"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list datasets: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{name}")
async def get_dataset(name: str, x_project_path: Optional[str] = Header(None)):
    try:
        project = _get_project_from_path(x_project_path)
        if not Dataset.exists(name):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset '{name}' not found")
        dataset = Dataset.load(name)
        return {"success": True, "dataset": _dataset_to_detail_response(dataset, project.path)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dataset: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/import")
async def import_dataset(
    files: List[UploadFile] = File(...),
    name: Optional[str] = Form(None),
    recursive: bool = Form(True),
    x_project_path: Optional[str] = Header(None)
):
    import os

    try:
        project = _get_project_from_path(x_project_path)
        if len(files) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files")

        temp_dir = Path(tempfile.mkdtemp(prefix="modelcub_import_"))
        original_cwd = os.getcwd()

        try:
            for upload_file in files:
                file_path = temp_dir / upload_file.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_bytes(await upload_file.read())

            os.chdir(project.path)

            req = ImportImagesRequest(source=temp_dir, name=name, copy=True, validate=True, recursive=recursive, force=False)
            code, message = import_images(req)

            if code != 0:
                raise RuntimeError(message)

            import re
            match = re.search(r'Name:\s+(\S+)', message)
            dataset_name = match.group(1) if match else name
            dataset = Dataset.load(dataset_name)

            return {
                "success": True,
                "message": f"Imported {dataset.images} images",
                "data": {"dataset": _dataset_to_response(dataset, project.path)}
            }
        finally:
            os.chdir(original_cwd)
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{name}")
async def delete_dataset(name: str, confirm: bool = False, x_project_path: Optional[str] = Header(None)):
    try:
        project = _get_project_from_path(x_project_path)
        if not confirm:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must confirm")
        if not Dataset.exists(name):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset '{name}' not found")
        dataset = Dataset.load(name)
        dataset.delete(confirm=True)
        return {"success": True, "message": f"Deleted '{name}'"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))