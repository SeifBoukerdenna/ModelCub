"""Annotation management API routes with null annotation support."""
from typing import List
import logging

from fastapi import APIRouter
from pydantic import BaseModel

from ..dependencies import ProjectRequired
from ...shared.api.schemas import APIResponse
from ...shared.api.errors import NotFoundError, ErrorCode
from ....services.annotation_service import (
    save_annotation,
    get_annotation,
    delete_annotation,
    SaveAnnotationRequest,
    GetAnnotationRequest,
    DeleteAnnotationRequest,
    BoundingBox,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets/{dataset_name}/annotations", tags=["Annotations"])


# ==================== REQUEST/RESPONSE MODELS ====================


class BoxModel(BaseModel):
    """Bounding box model"""
    class_id: int
    x: float
    y: float
    w: float
    h: float


class SaveAnnotationsRequest(BaseModel):
    """Request to save annotations"""
    boxes: List[BoxModel]
    is_null: bool = False  # Mark as null (intentionally empty)


class AnnotationResponse(BaseModel):
    """Annotation response"""
    image_id: str
    image_path: str
    split: str
    boxes: List[BoxModel]
    num_boxes: int
    is_null: bool  # Whether marked as null
    is_annotated: bool  # Whether has any annotation (boxes or null marker)


# ==================== ENDPOINTS ====================


@router.get("/{image_id}")
async def get_annotations(
    dataset_name: str,
    image_id: str,
    project: ProjectRequired
) -> APIResponse[AnnotationResponse]:
    """Get annotations for an image."""
    try:
        logger.info(f"Getting annotations for {dataset_name}/{image_id}")

        req = GetAnnotationRequest(
            dataset_name=dataset_name,
            image_id=image_id,
            project_path=project.path
        )

        result = get_annotation(req)

        if not result.success:
            raise NotFoundError(
                message=result.message,
                code=ErrorCode.DATASET_NOT_FOUND
            )

        data = result.data
        return APIResponse(
            success=True,
            data=AnnotationResponse(**data),
            message=f"Retrieved annotation (boxes={data['num_boxes']}, null={data['is_null']})"
        )

    except Exception as e:
        logger.error(f"Failed to get annotations: {e}", exc_info=True)
        raise


@router.post("/{image_id}")
async def save_annotations(
    dataset_name: str,
    image_id: str,
    request: SaveAnnotationsRequest,
    project: ProjectRequired
) -> APIResponse[dict]:
    """Save annotations for an image."""
    try:
        logger.info(f"Saving annotation for {dataset_name}/{image_id} (boxes={len(request.boxes)}, null={request.is_null})")

        # Convert to BoundingBox objects
        boxes = [
            BoundingBox(
                class_id=box.class_id,
                x=box.x,
                y=box.y,
                w=box.w,
                h=box.h
            )
            for box in request.boxes
        ]

        req = SaveAnnotationRequest(
            dataset_name=dataset_name,
            image_id=image_id,
            boxes=boxes,
            project_path=project.path,
            is_null=request.is_null
        )

        result = save_annotation(req)

        if not result.success:
            raise NotFoundError(
                message=result.message,
                code=ErrorCode.DATASET_NOT_FOUND
            )

        return APIResponse(
            success=True,
            data=result.data,
            message=result.message
        )

    except Exception as e:
        logger.error(f"Failed to save annotations: {e}", exc_info=True)
        raise


@router.delete("/{image_id}/boxes/{box_index}")
async def delete_box(
    dataset_name: str,
    image_id: str,
    box_index: int,
    project: ProjectRequired
) -> APIResponse[dict]:
    """Delete a specific bounding box."""
    try:
        logger.info(f"Deleting box {box_index} from {dataset_name}/{image_id}")

        req = DeleteAnnotationRequest(
            dataset_name=dataset_name,
            image_id=image_id,
            box_index=box_index,
            project_path=project.path
        )

        result = delete_annotation(req)

        if not result.success:
            raise NotFoundError(
                message=result.message,
                code=ErrorCode.DATASET_NOT_FOUND
            )

        return APIResponse(
            success=True,
            data=result.data,
            message=result.message
        )

    except Exception as e:
        logger.error(f"Failed to delete box: {e}", exc_info=True)
        raise