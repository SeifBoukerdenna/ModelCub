"""Model training API routes - Refactored."""
from typing import List
import logging

from fastapi import APIRouter

from ..dependencies import ProjectOptional
from ...shared.api.config import Endpoints
from ...shared.api.schemas import APIResponse, Model

logger = logging.getLogger(__name__)
router = APIRouter(prefix=Endpoints.MODELS, tags=["Models"])


@router.get("")
async def list_models(project: ProjectOptional) -> APIResponse[List[Model]]:
    """List available models."""
    logger.info("Listing models")

    # Placeholder - will be implemented when training is added
    return APIResponse(
        success=True,
        data=[],
        message="Model operations coming soon"
    )


@router.get("/{model_id}")
async def get_model(
    model_id: str,
    project: ProjectOptional
) -> APIResponse[Model]:
    """Get model details."""
    logger.info(f"Getting model: {model_id}")

    # Placeholder
    return APIResponse(
        success=True,
        data=None,
        message="Model operations coming soon"
    )