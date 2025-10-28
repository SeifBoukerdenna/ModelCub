"""
Training runs API routes.
"""
from pathlib import Path

from typing import List, Optional, Dict, Any
import logging

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..dependencies import ProjectRequired
from ...shared.api.config import Endpoints
from ...shared.api.schemas import APIResponse
from ....services.training.training_service import TrainingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/runs", tags=["Runs"])


class CreateRunRequest(BaseModel):
    """Request model for creating a training run."""
    dataset_name: str
    model: str = "yolov8n"
    epochs: int = 100
    task: str = "detect"
    imgsz: int = 640
    batch: int = 16
    device: str = "auto"
    patience: int = 50
    save_period: int = 10
    workers: int = 8
    seed: Optional[int] = None


@router.post("")
async def create_run(
    request: CreateRunRequest,
    project: ProjectRequired
) -> APIResponse[Dict[str, Any]]:
    """Create a new training run."""
    logger.info(f"Creating run for dataset: {request.dataset_name}")

    try:
        service = TrainingService(project.path)

        # Create run
        run_id = service.create_run(
            dataset_name=request.dataset_name,
            model=request.model,
            epochs=request.epochs,
            task=request.task,
            imgsz=request.imgsz,
            batch=request.batch,
            device=request.device,
            patience=request.patience,
            save_period=request.save_period,
            workers=request.workers,
            seed=request.seed
        )

        # Get created run
        run = service.get_status(run_id)

        logger.info(f"Created run: {run_id}")

        return APIResponse(
            success=True,
            data=run,
            message=f"Run {run_id} created successfully"
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create run: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to create run: {str(e)}"
        )


@router.get("")
async def list_runs(
    project: ProjectRequired,
    status: Optional[str] = None
) -> APIResponse[List[Dict[str, Any]]]:
    """List all training runs with optional status filter."""
    logger.info(f"Listing runs for project: {project.path}, status={status}")

    try:
        service = TrainingService(project.path)
        runs = service.list_runs(status=status)

        # Sort by created date (newest first)
        runs.sort(key=lambda r: r.get('created', ''), reverse=True)

        logger.info(f"Found {len(runs)} runs")

        return APIResponse(
            success=True,
            data=runs,
            message=f"Found {len(runs)} run(s)"
        )

    except Exception as e:
        logger.error(f"Failed to list runs: {e}")
        return APIResponse(
            success=False,
            data=[],
            message=f"Failed to list runs: {str(e)}"
        )


@router.get("/{run_id}")
async def get_run(
    run_id: str,
    project: ProjectRequired
) -> APIResponse[Optional[Dict[str, Any]]]:
    """Get training run details."""
    logger.info(f"Getting run: {run_id}")

    try:
        service = TrainingService(project.path)
        run = service.get_status(run_id)

        return APIResponse(
            success=True,
            data=run,
            message="Run retrieved successfully"
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get run {run_id}: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to get run: {str(e)}"
        )


@router.post("/{run_id}/start")
async def start_run(
    run_id: str,
    project: ProjectRequired
) -> APIResponse[Dict[str, Any]]:
    """Start a pending training run."""
    logger.info(f"Starting run: {run_id}")

    try:
        service = TrainingService(project.path)
        service.start_run(run_id)
        run = service.get_status(run_id)

        return APIResponse(
            success=True,
            data=run,
            message=f"Run {run_id} started successfully"
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to start run {run_id}: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to start run: {str(e)}"
        )


@router.post("/{run_id}/stop")
async def stop_run(
    run_id: str,
    project: ProjectRequired,
    timeout: float = 10.0
) -> APIResponse[Dict[str, Any]]:
    """Stop a running training run."""
    logger.info(f"Stopping run: {run_id}")

    try:
        service = TrainingService(project.path)
        service.stop_run(run_id, timeout=timeout)
        run = service.get_status(run_id)

        return APIResponse(
            success=True,
            data=run,
            message=f"Run {run_id} stopped successfully"
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data=None,
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to stop run {run_id}: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to stop run: {str(e)}"
        )


@router.delete("/{run_id}")
async def delete_run(
    run_id: str,
    project: ProjectRequired,
    keep_artifacts: bool = False
) -> APIResponse[None]:
    """Delete a training run."""
    logger.info(f"Deleting run: {run_id}, keep_artifacts={keep_artifacts}")

    try:
        service = TrainingService(project.path)
        run = service.get_status(run_id)

        if run['status'] == 'running':
            return APIResponse(
                success=False,
                data=None,
                message="Cannot delete running run. Stop it first."
            )

        # Delete artifacts if requested
        if not keep_artifacts:
            import shutil
            run_path = project.path / run['artifacts_path']
            if run_path.exists():
                shutil.rmtree(run_path)

        # Remove from registry
        service.run_registry.remove_run(run_id)

        logger.info(f"Successfully deleted run: {run_id}")

        return APIResponse(
            success=True,
            data=None,
            message=f"Run '{run_id}' deleted successfully"
        )

    except Exception as e:
        logger.error(f"Failed to delete run {run_id}: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Failed to delete run: {str(e)}"
        )

@router.get("/{run_id}/logs")
async def get_logs(
    run_id: str,
    project: ProjectRequired,
    stream: str = Query(default="stdout", regex="^(stdout|stderr)$"),
    lines: int = Query(default=100, ge=1, le=10000)
) -> APIResponse[Dict[str, Any]]:
    """Get training run logs."""
    logger.info(f"Getting logs for run: {run_id}, stream={stream}, lines={lines}")

    try:
        service = TrainingService(project.path)
        run = service.get_status(run_id)

        # Get log file path
        log_file = project.path / run['artifacts_path'] / 'logs' / f'{stream}.log'

        if not log_file.exists():
            return APIResponse(
                success=True,
                data={'logs': [], 'exists': False},
                message=f"Log file not found: {stream}.log"
            )

        # Read last N lines
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            log_lines = all_lines[-lines:] if lines else all_lines

        return APIResponse(
            success=True,
            data={
                'logs': [line.rstrip() for line in log_lines],
                'exists': True,
                'total_lines': len(all_lines)
            },
            message=f"Retrieved {len(log_lines)} log lines"
        )

    except ValueError as e:
        return APIResponse(
            success=False,
            data={'logs': [], 'exists': False},
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get logs for run {run_id}: {e}")
        return APIResponse(
            success=False,
            data={'logs': [], 'exists': False},
            message=f"Failed to get logs: {str(e)}"
        )