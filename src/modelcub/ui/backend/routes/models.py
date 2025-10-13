"""
Model training API routes - SDK-ready implementation.

Prepared to use SDK when training features are implemented.
"""
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
    """
    List available models.

    Will use SDK: project.runs.list_runs() when implemented.
    """
    logger.info("Listing models")

    # TODO: When training is implemented, use:
    # runs = project.runs.list_runs()
    # models = [_run_to_model_schema(run) for run in runs]

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
    """
    Get model details.

    Will use SDK: project.runs.get_run(model_id) when implemented.
    """
    logger.info(f"Getting model: {model_id}")

    # TODO: When training is implemented, use:
    # run = project.runs.get_run(model_id)
    # model = _run_to_model_schema(run)

    return APIResponse(
        success=True,
        data=None,
        message="Model operations coming soon"
    )