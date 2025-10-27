"""
Model management API routes.
"""
from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter

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
        'run_id': model_data['run_id'],
        'path': model_data['path'],
        'description': metadata.get('description', ''),
        'tags': metadata.get('tags', []),
        'metrics': metadata.get('metrics', {}),
        'dataset_name': metadata.get('dataset_name', ''),
        'config': metadata.get('config', {})
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
        model_data = model_registry.get_model(name)

        if not model_data:
            return APIResponse(
                success=False,
                data=None,
                message=f"Model not found: {name}"
            )

        formatted_model = _format_model_response(model_data)

        return APIResponse(
            success=True,
            data=formatted_model,
            message="Model retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Failed to get model {name}: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to get model: {str(e)}"
        )


@router.delete("/{name}")
async def delete_model(
    name: str,
    project: ProjectRequired
) -> APIResponse[None]:
    """Delete a promoted model."""
    logger.info(f"Deleting model: {name}")

    try:
        model_registry = ModelRegistry(project.path)

        # Check if model exists
        model_data = model_registry.get_model(name)
        if not model_data:
            return APIResponse(
                success=False,
                data=None,
                message=f"Model not found: {name}"
            )

        # Delete model
        model_registry.remove_model(name)

        logger.info(f"Successfully deleted model: {name}")

        return APIResponse(
            success=True,
            data=None,
            message=f"Model '{name}' deleted successfully"
        )

    except Exception as e:
        logger.error(f"Failed to delete model {name}: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to delete model: {str(e)}"
        )