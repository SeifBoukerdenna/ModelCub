"""
Predictions/Inference routes for ModelCub UI.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File
from pathlib import Path

from ..dependencies import ProjectRequired
from ...shared.api.config import Endpoints
from ...shared.api.schemas import APIResponse, ResponseMeta
from ...shared.api.errors import BadRequestError, NotFoundError, ErrorCode
from ....services.inference import InferenceService
from ....core.registries import DatasetRegistry

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.get("")
async def list_predictions(
    project: ProjectRequired,
    status: Optional[str] = None
) -> APIResponse[List[dict]]:
    """List all inference jobs."""
    logger.info(f"Listing predictions for project: {project.name}")

    try:
        service = InferenceService(project.path)
        jobs = service.list_inferences(status=status)

        return APIResponse(
            success=True,
            data=jobs,
            message=f"Found {len(jobs)} prediction job(s)",
            meta=ResponseMeta()
        )
    except Exception as e:
        logger.error(f"Failed to list predictions: {e}")
        return APIResponse(
            success=False,
            data=[],
            message=f"Failed to list predictions: {str(e)}"
        )


@router.get("/{inference_id}")
async def get_prediction(
    inference_id: str,
    project: ProjectRequired
) -> APIResponse[dict]:
    """Get prediction job details and results."""
    logger.info(f"Getting prediction: {inference_id}")

    try:
        service = InferenceService(project.path)
        result = service.get_results(inference_id)

        if not result:
            raise NotFoundError(
                message=f"Prediction not found: {inference_id}",
                code=ErrorCode.NOT_FOUND
            )

        return APIResponse(
            success=True,
            data=result,
            message="Prediction retrieved successfully"
        )
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get prediction: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to get prediction: {str(e)}"
        )


@router.post("")
async def create_prediction(
    project: ProjectRequired,
    model_name: str,
    input_type: str,
    input_path: str,
    conf: float = 0.25,
    iou: float = 0.45,
    device: str = "cpu",
    batch_size: int = 16,
    save_txt: bool = True,
    save_img: bool = False,
    classes: Optional[str] = None,
    split: Optional[str] = "val"
) -> APIResponse[dict]:
    """
    Create and run inference job.

    Args:
        model_name: Model name to use
        input_type: 'image', 'images', or 'dataset'
        input_path: Path to input (relative to project)
        conf: Confidence threshold (0-1)
        iou: IoU threshold (0-1)
        device: Device (cpu, cuda, mps)
        batch_size: Batch size
        save_txt: Save YOLO labels
        save_img: Save annotated images
        classes: Comma-separated class IDs to filter
        split: Dataset split (for dataset type)
    """
    logger.info(f"Creating prediction: {model_name} on {input_path}")

    try:
        service = InferenceService(project.path)

        # Validate input
        if input_type not in ['image', 'images', 'dataset']:
            raise BadRequestError(
                message=f"Invalid input_type: {input_type}",
                code=ErrorCode.VALIDATION_ERROR
            )

        # Parse classes
        class_list = None
        if classes:
            try:
                class_list = [int(c.strip()) for c in classes.split(',')]
            except ValueError:
                raise BadRequestError(
                    message="Invalid classes format. Use comma-separated integers.",
                    code=ErrorCode.VALIDATION_ERROR
                )

        # For dataset input, validate and adjust path
        if input_type == 'dataset':
            dataset_registry = DatasetRegistry(project.path)
            if not dataset_registry.exists(input_path):
                raise NotFoundError(
                    message=f"Dataset not found: {input_path}",
                    code=ErrorCode.NOT_FOUND
                )
            input_path = str(project.path / "data" / "datasets" / input_path)

        # Create inference job
        inference_id = service.create_inference_job(
            model_identifier=model_name,
            input_type=input_type,
            input_path=input_path,
            conf_threshold=conf,
            iou_threshold=iou,
            device=device,
            save_txt=save_txt,
            save_img=save_img,
            classes=class_list,
            batch_size=batch_size
        )

        # Run inference (async in production, sync for now)
        stats = service.run_inference(inference_id)

        # Get final job data
        job = service.inference_registry.get_inference(inference_id)

        return APIResponse(
            success=True,
            data={
                'inference_id': inference_id,
                'stats': stats,
                'job': job
            },
            message="Inference completed successfully"
        )

    except (BadRequestError, NotFoundError):
        raise
    except FileNotFoundError as e:
        raise NotFoundError(
            message=str(e),
            code=ErrorCode.NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to run inference: {e}", exc_info=True)
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to run inference: {str(e)}"
        )


@router.delete("/{inference_id}")
async def delete_prediction(
    inference_id: str,
    project: ProjectRequired
) -> APIResponse[None]:
    """Delete a prediction job."""
    logger.info(f"Deleting prediction: {inference_id}")

    try:
        service = InferenceService(project.path)
        job = service.inference_registry.get_inference(inference_id)

        if not job:
            raise NotFoundError(
                message=f"Prediction not found: {inference_id}",
                code=ErrorCode.NOT_FOUND
            )

        # Delete output directory
        output_path = project.path / job['output_path']
        if output_path.exists():
            import shutil
            shutil.rmtree(output_path)

        # Remove from registry
        service.inference_registry.remove_inference(inference_id)

        return APIResponse(
            success=True,
            data=None,
            message=f"Prediction '{inference_id}' deleted successfully"
        )

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to delete prediction: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to delete prediction: {str(e)}"
        )