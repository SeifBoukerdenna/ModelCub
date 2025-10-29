from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import tempfile
import shutil

from fastapi import APIRouter, UploadFile, File, Form

from ..dependencies import ProjectRequired
from ...shared.api.config import Endpoints
from ...shared.api.schemas import APIResponse
from ....core.registries import ModelRegistry

logger = logging.getLogger(__name__)
router = APIRouter(prefix=Endpoints.MODELS, tags=["Models"])


def _format_model_response(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format model data for API response."""
    metadata = model_data.get('metadata', {})

    return {
        'name': model_data['name'],
        'version': model_data['version'],
        'created': model_data['created'],
        'run_id': model_data.get('run_id'),
        'path': model_data['path'],
        'provenance': model_data.get('provenance', 'promoted'),
        'description': metadata.get('description', ''),
        'tags': metadata.get('tags', []),
        'metrics': metadata.get('metrics', {}),
        'dataset_name': metadata.get('dataset_name', ''),
        'config': metadata.get('config', {}),
        'classes': metadata.get('classes', []),
        'num_classes': metadata.get('num_classes', 0),
        'task': metadata.get('task', 'detect'),
    }


@router.get("")
async def list_models(project: ProjectRequired) -> APIResponse[List[Dict[str, Any]]]:
    """List all promoted models."""
    logger.info(f"Listing models for project: {project.path}")

    try:
        model_registry = ModelRegistry(project.path)
        models = model_registry.list_models()

        formatted_models = [_format_model_response(m) for m in models]
        formatted_models.sort(key=lambda m: m['created'], reverse=True)

        logger.info(f"Found {len(formatted_models)} models")

        return APIResponse(
            success=True,
            data=formatted_models,
            message=f"Found {len(formatted_models)} model(s)"
        )

    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return APIResponse(
            success=False,
            data=[],
            message=f"Failed to list models: {str(e)}"
        )


@router.get("/{name}")
async def get_model(
    name: str,
    project: ProjectRequired
) -> APIResponse[Optional[Dict[str, Any]]]:
    """Get model details by name."""
    logger.info(f"Getting model: {name}")

    try:
        model_registry = ModelRegistry(project.path)
        model = model_registry.get_model(name)

        if not model:
            return APIResponse(
                success=False,
                data=None,
                message=f"Model not found: {name}"
            )

        return APIResponse(
            success=True,
            data=_format_model_response(model),
            message=f"Model '{name}' loaded successfully"
        )

    except Exception as e:
        logger.error(f"Failed to get model: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to get model: {str(e)}"
        )

@router.post("/import")
async def import_model(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    validate_model: bool = Form(True),  # CHANGED: validate -> validate_model
    project: ProjectRequired = None
) -> APIResponse[Dict[str, Any]]:
    """
    Import a model from uploaded .pt file.

    Args:
        file: Model file (.pt)
        name: Model name
        description: Model description
        tags: Comma-separated tags
        validate_model: Whether to validate model before import
        project: Project dependency

    Returns:
        APIResponse with imported model info
    """
    logger.info(f"Importing model: {name} from file: {file.filename}")

    if not file.filename or not file.filename.endswith('.pt'):
        return APIResponse(
            success=False,
            data=None,
            message="Invalid file type. Only .pt files are supported."
        )

    temp_file = None
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = Path(temp_file.name)

        logger.info(f"Saved temp file: {temp_path}")

        # Import using ModelImportService
        from ....services.model_import_service import ModelImportService

        service = ModelImportService(project.path)

        # Parse tags
        tag_list = None
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]

        # Import model
        model_info = service.import_model(
            source_path=temp_path,
            name=name,
            description=description,
            tags=tag_list,
            validate=validate_model  # CHANGED: pass validate_model here
        )

        logger.info(f"Model imported successfully: {name}")

        return APIResponse(
            success=True,
            data=_format_model_response(model_info),
            message=f"Model '{name}' imported successfully"
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to import model: {e}", exc_info=True)
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to import model: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_file and Path(temp_file.name).exists():
            try:
                Path(temp_file.name).unlink()
                logger.info("Cleaned up temp file")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")


@router.delete("/{name}")
async def delete_model(
    name: str,
    project: ProjectRequired
) -> APIResponse[None]:
    """Delete a promoted model."""
    logger.info(f"Deleting model: {name}")

    try:
        model_registry = ModelRegistry(project.path)
        model_registry.remove_model(name)

        logger.info(f"Model deleted successfully: {name}")

        return APIResponse(
            success=True,
            data=None,
            message=f"Model '{name}' deleted successfully"
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to delete model: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to delete model: {str(e)}"
        )