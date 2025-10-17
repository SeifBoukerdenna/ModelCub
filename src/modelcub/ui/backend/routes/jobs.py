"""Annotation job management API routes."""
from typing import List, Optional
import logging
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from datetime import datetime

from ..dependencies import ProjectRequired
from ...shared.api.config import Endpoints
from ...shared.api.schemas import APIResponse
from ...shared.api.errors import NotFoundError, ErrorCode
from ....services.annotation_job_manager import (
    AnnotationJobManager,
    JobStatus,
    TaskStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix=Endpoints.JOBS, tags=["Jobs"])


# ==================== REQUEST/RESPONSE MODELS ====================


class CreateJobRequest(BaseModel):
    """Request to create annotation job"""
    dataset_name: str
    image_ids: Optional[List[str]] = None
    auto_start: bool = True
    config: Optional[dict] = None


class JobResponse(BaseModel):
    """Job status response"""
    job_id: str
    dataset_name: str
    status: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    paused_at: Optional[str] = None
    can_resume: bool
    is_terminal: bool


class TaskResponse(BaseModel):
    """Task response"""
    task_id: str
    job_id: str
    image_id: str
    image_path: str
    status: str
    attempts: int
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


# ==================== HELPER FUNCTIONS ====================


def _get_job_manager(project_path: Path) -> AnnotationJobManager:
    """Get job manager instance"""
    return AnnotationJobManager(project_path, num_workers=4)


def _job_to_response(job) -> JobResponse:
    """Convert job to response model"""
    return JobResponse(
        job_id=job.job_id,
        dataset_name=job.dataset_name,
        status=job.status.value,
        total_tasks=job.total_tasks,
        completed_tasks=job.completed_tasks,
        failed_tasks=job.failed_tasks,
        created_at=job.created_at.isoformat(),
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        paused_at=job.paused_at.isoformat() if job.paused_at else None,
        can_resume=job.can_resume,
        is_terminal=job.is_terminal,
    )


def _task_to_response(task) -> TaskResponse:
    """Convert task to response model"""
    return TaskResponse(
        task_id=task.task_id,
        job_id=task.job_id,
        image_id=task.image_id,
        image_path=task.image_path,
        status=task.status.value,
        attempts=task.attempts,
        error_message=task.error_message,
        started_at=task.started_at.isoformat() if task.started_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


# ==================== ENDPOINTS ====================


@router.post("/create")
async def create_job(
    request: CreateJobRequest,
    project: ProjectRequired
) -> APIResponse[JobResponse]:
    """Create and optionally start annotation job"""
    try:
        logger.info(f"Creating job for dataset: {request.dataset_name}")
        manager = _get_job_manager(project.path)

        job = manager.create_job(
            dataset_name=request.dataset_name,
            image_ids=request.image_ids,
            config=request.config
        )

        if request.auto_start:
            job = manager.start_job(job.job_id)
            logger.info(f"Started job: {job.job_id}")

        return APIResponse(
            success=True,
            data=_job_to_response(job),
            message=f"Job created: {job.job_id}"
        )
    except ValueError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.DATASET_NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to create job: {e}", exc_info=True)
        raise


@router.get("")
async def list_jobs(
    project: ProjectRequired,
    status: Optional[str] = None
) -> APIResponse[List[JobResponse]]:
    """List all jobs, optionally filtered by status"""
    try:
        manager = _get_job_manager(project.path)

        job_status = JobStatus(status) if status else None
        jobs = manager.list_jobs(job_status)

        return APIResponse(
            success=True,
            data=[_job_to_response(job) for job in jobs],
            message=f"Found {len(jobs)} job(s)"
        )
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}", exc_info=True)
        raise


@router.get("/{job_id}")
async def get_job(
    job_id: str,
    project: ProjectRequired
) -> APIResponse[JobResponse]:
    """Get job status"""
    try:
        manager = _get_job_manager(project.path)
        job = manager.get_job(job_id)

        if not job:
            raise NotFoundError(
                message=f"Job not found: {job_id}",
                code=ErrorCode.DATASET_NOT_FOUND  # Reusing error code
            )

        return APIResponse(
            success=True,
            data=_job_to_response(job),
            message="Job retrieved"
        )
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get job: {e}", exc_info=True)
        raise


@router.post("/{job_id}/start")
async def start_job(
    job_id: str,
    project: ProjectRequired
) -> APIResponse[JobResponse]:
    """Start or resume a job"""
    try:
        manager = _get_job_manager(project.path)
        job = manager.start_job(job_id)

        return APIResponse(
            success=True,
            data=_job_to_response(job),
            message=f"Job started: {job_id}"
        )
    except ValueError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.DATASET_NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to start job: {e}", exc_info=True)
        raise


@router.post("/{job_id}/pause")
async def pause_job(
    job_id: str,
    project: ProjectRequired
) -> APIResponse[JobResponse]:
    """Pause a running job"""
    try:
        manager = _get_job_manager(project.path)
        job = manager.pause_job(job_id)

        return APIResponse(
            success=True,
            data=_job_to_response(job),
            message=f"Job paused: {job_id}"
        )
    except ValueError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.DATASET_NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to pause job: {e}", exc_info=True)
        raise


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    project: ProjectRequired
) -> APIResponse[JobResponse]:
    """Cancel a job"""
    try:
        manager = _get_job_manager(project.path)
        job = manager.cancel_job(job_id)

        return APIResponse(
            success=True,
            data=_job_to_response(job),
            message=f"Job cancelled: {job_id}"
        )
    except ValueError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.DATASET_NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to cancel job: {e}", exc_info=True)
        raise

@router.post("/{job_id}/tasks/{task_id}/complete")
async def complete_task(
    job_id: str,
    task_id: str,
    project: ProjectRequired
) -> APIResponse[TaskResponse]:
    """Mark a task as completed (for testing)."""
    try:
        manager = _get_job_manager(project.path)

        # Get the task
        tasks = manager.get_tasks(job_id)
        task = next((t for t in tasks if t.task_id == task_id), None)

        if not task:
            raise NotFoundError(message="Task not found", code=ErrorCode.DATASET_NOT_FOUND)

        # Mark as completed
        from modelcub.services.annotation_job_manager import TaskStatus
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        manager.store.save_task(task)

        # Update job counters
        job = manager.get_job(job_id)
        if job:
            job.completed_tasks += 1
            manager.store.save_job(job)

        return APIResponse(
            success=True,
            data=_task_to_response(task),
            message="Task marked as completed"
        )
    except Exception as e:
        logger.error(f"Failed to complete task: {e}", exc_info=True)
        raise


@router.get("/{job_id}/tasks")
async def get_tasks(
    job_id: str,
    project: ProjectRequired,
    status: Optional[str] = None
) -> APIResponse[List[TaskResponse]]:
    """Get tasks for a job"""
    try:
        manager = _get_job_manager(project.path)

        task_status = TaskStatus(status) if status else None
        tasks = manager.get_tasks(job_id, task_status)

        return APIResponse(
            success=True,
            data=[_task_to_response(task) for task in tasks],
            message=f"Found {len(tasks)} task(s)"
        )
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}", exc_info=True)
        raise


@router.get("/{job_id}/next-task")
async def get_next_task(
    job_id: str,
    project: ProjectRequired
) -> APIResponse[Optional[TaskResponse]]:
    """Get next pending task for annotation"""
    try:
        manager = _get_job_manager(project.path)
        tasks = manager.get_tasks(job_id, TaskStatus.PENDING)

        if not tasks:
            return APIResponse(
                success=True,
                data=None,
                message="No more tasks"
            )

        return APIResponse(
            success=True,
            data=_task_to_response(tasks[0]),
            message="Next task retrieved"
        )
    except Exception as e:
        logger.error(f"Failed to get next task: {e}", exc_info=True)
        raise