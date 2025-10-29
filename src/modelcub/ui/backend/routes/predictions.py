"""
Predictions/Inference routes for ModelCub UI.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse

from ..dependencies import ProjectRequired
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
        return APIResponse(success=False, data=[], message=f"Failed to list predictions: {str(e)}")


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
    """Create and run inference job."""
    try:
        service = InferenceService(project.path)

        if input_type not in ['image', 'images', 'dataset']:
            raise BadRequestError(
                message=f"Invalid input_type: {input_type}",
                code=ErrorCode.VALIDATION_ERROR
            )

        class_list = None
        if classes:
            try:
                class_list = [int(c.strip()) for c in classes.split(',')]
            except ValueError:
                raise BadRequestError(
                    message="Invalid classes format. Use comma-separated integers.",
                    code=ErrorCode.VALIDATION_ERROR
                )

        if input_type == 'dataset':
            dataset_registry = DatasetRegistry(project.path)
            if not dataset_registry.exists(input_path):
                raise NotFoundError(message=f"Dataset not found: {input_path}", code=ErrorCode.NOT_FOUND)
            input_path = str(project.path / "data" / "datasets" / input_path)

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

        stats = service.run_inference(inference_id)
        job = service.inference_registry.get_inference(inference_id)

        return APIResponse(
            success=True,
            data={'inference_id': inference_id, 'stats': stats, 'job': job},
            message="Inference completed successfully"
        )

    except (BadRequestError, NotFoundError):
        raise
    except FileNotFoundError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to run inference: {e}", exc_info=True)
        return APIResponse(success=False, data=None, message=f"Failed to run inference: {str(e)}")


@router.delete("/{inference_id}")
async def delete_prediction(
    inference_id: str,
    project: ProjectRequired
) -> APIResponse[None]:
    """Delete a prediction job."""
    try:
        service = InferenceService(project.path)
        job = service.inference_registry.get_inference(inference_id)

        if not job:
            raise NotFoundError(message=f"Prediction not found: {inference_id}", code=ErrorCode.NOT_FOUND)

        output_path = project.path / job['output_path']
        if output_path.exists():
            import shutil
            shutil.rmtree(output_path)

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
        return APIResponse(success=False, data=None, message=f"Failed to delete prediction: {str(e)}")


@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    project: ProjectRequired = None
) -> APIResponse[dict]:
    """Upload files for inference."""
    import shutil
    from datetime import datetime

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        upload_dir = project.path / "data" / "uploads" / "predictions" / timestamp
        upload_dir.mkdir(parents=True, exist_ok=True)

        saved_files = []
        file_paths = []

        for upload_file in files:
            filename = upload_file.filename or "uploaded_file"
            file_path = upload_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'wb') as f:
                shutil.copyfileobj(upload_file.file, f)

            saved_files.append(filename)
            file_paths.append(file_path)

        if len(file_paths) == 1:
            relative_path = str(file_paths[0].relative_to(project.path))
        else:
            relative_path = str(upload_dir.relative_to(project.path))

        return APIResponse(
            success=True,
            data={'path': relative_path, 'files': saved_files, 'count': len(saved_files)},
            message=f"Uploaded {len(saved_files)} file(s) successfully"
        )
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        return APIResponse(success=False, data=None, message=f"Upload failed: {str(e)}")


@router.get("/{inference_id}/results")
async def get_prediction_results(
    inference_id: str,
    project: ProjectRequired
) -> APIResponse[dict]:
    """Get prediction results with output image list."""
    try:
        service = InferenceService(project.path)
        job = service.inference_registry.get_inference(inference_id)

        if not job:
            raise NotFoundError(message=f"Prediction not found: {inference_id}", code=ErrorCode.NOT_FOUND)

        output_images = []
        if job['config'].get('save_img'):
            output_path = project.path / job['output_path']
            images_dir = output_path / 'images'
            if images_dir.exists():
                for ext in ['*.jpg', '*.jpeg', '*.png']:
                    output_images.extend([f.name for f in images_dir.glob(ext)])

        return APIResponse(
            success=True,
            data={**job, 'output_images': sorted(output_images)},
            message="Results retrieved successfully"
        )
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get results: {e}")
        return APIResponse(success=False, data=None, message=f"Failed to get results: {str(e)}")


@router.get("/{inference_id}/images/{image_name:path}")
async def serve_prediction_image(
    inference_id: str,
    image_name: str,
    project: ProjectRequired
):
    """Serve a prediction output image."""
    try:
        service = InferenceService(project.path)
        job = service.inference_registry.get_inference(inference_id)

        if not job:
            raise NotFoundError(message=f"Prediction not found: {inference_id}", code=ErrorCode.NOT_FOUND)

        output_path = project.path / job['output_path']
        image_path = output_path / 'images' / image_name

        if not image_path.exists():
            raise NotFoundError(message=f"Image not found: {image_name}", code=ErrorCode.FILE_NOT_FOUND)

        return FileResponse(image_path)
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to serve image: {e}")
        raise NotFoundError(message=f"Failed to serve image: {str(e)}", code=ErrorCode.FILE_NOT_FOUND)