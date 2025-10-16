"""
ModelCub SDK - Job Management.

High-level Python API for annotation jobs.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime

from ..services.annotation_job_manager import (
    AnnotationJobManager,
    AnnotationJob,
    AnnotationTask,
    JobStatus,
    TaskStatus
)
from ..core.paths import project_root


class Job:
    """
    High-level interface for annotation jobs.

    Example:
        >>> job = Job.load("abc123")
        >>> job.start()
        >>> job.wait()
    """

    def __init__(self, job_data: AnnotationJob, manager: AnnotationJobManager):
        self._data = job_data
        self._manager = manager

    @property
    def id(self) -> str:
        return self._data.job_id

    @property
    def dataset_name(self) -> str:
        return self._data.dataset_name

    @property
    def status(self) -> JobStatus:
        return self._data.status

    @property
    def progress(self) -> float:
        return self._data.progress

    @property
    def total_tasks(self) -> int:
        return self._data.total_tasks

    @property
    def completed_tasks(self) -> int:
        return self._data.completed_tasks

    @property
    def failed_tasks(self) -> int:
        return self._data.failed_tasks

    @property
    def is_complete(self) -> bool:
        return self._data.is_terminal

    @property
    def created_at(self) -> datetime:
        return self._data.created_at

    def start(self) -> Job:
        """Start or resume the job."""
        self._data = self._manager.start_job(self.id)
        return self

    def pause(self) -> Job:
        """Pause the job."""
        self._data = self._manager.pause_job(self.id)
        return self

    def cancel(self) -> Job:
        """Cancel the job."""
        self._data = self._manager.cancel_job(self.id)
        return self

    def refresh(self) -> Job:
        """Refresh job data from database."""
        self._data = self._manager.get_job(self.id)
        return self

    def wait(self, poll_interval: float = 1.0) -> Job:
        """Wait for job to complete."""
        import time
        while not self._data.is_terminal:
            time.sleep(poll_interval)
            self.refresh()
        return self

    def get_tasks(self, status: Optional[TaskStatus] = None) -> List[AnnotationTask]:
        """Get tasks for this job."""
        return self._manager.get_tasks(self.id, status)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "dataset_name": self.dataset_name,
            "status": self.status.value,
            "progress": self.progress,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def load(cls, job_id: str, project_path: Optional[Path] = None) -> Job:
        """Load job by ID."""
        if project_path is None:
            project_path = project_root()

        manager = AnnotationJobManager(project_path)
        job_data = manager.get_job(job_id)

        if not job_data:
            raise ValueError(f"Job not found: {job_id}")

        return cls(job_data, manager)

    def __repr__(self) -> str:
        return f"Job(id='{self.id}', status='{self.status.value}', progress={self.progress:.1f}%)"


class JobManager:
    """
    High-level interface for managing annotation jobs.

    Example:
        >>> manager = JobManager.load()
        >>> job = manager.create_job("my-dataset")
        >>> job.start()
    """

    def __init__(self, project_path: Optional[Path] = None, num_workers: int = 4):
        if project_path is None:
            project_path = project_root()

        self.project_path = project_path
        self._manager = AnnotationJobManager(project_path, num_workers=num_workers)

    @classmethod
    def load(cls, project_path: Optional[Path] = None, num_workers: int = 4) -> JobManager:
        """Load job manager for current project."""
        return cls(project_path, num_workers)

    def create_job(
        self,
        dataset_name: str,
        image_ids: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        auto_start: bool = False
    ) -> Job:
        """Create a new annotation job."""
        job_data = self._manager.create_job(dataset_name, image_ids, config)
        job = Job(job_data, self._manager)

        if auto_start:
            job.start()

        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        job_data = self._manager.get_job(job_id)
        if not job_data:
            return None
        return Job(job_data, self._manager)

    def list_jobs(self, status: Optional[JobStatus] = None) -> List[Job]:
        """List all jobs, optionally filtered by status."""
        jobs_data = self._manager.list_jobs(status)
        return [Job(jd, self._manager) for jd in jobs_data]

    def set_task_handler(self, handler: Callable) -> None:
        """Set custom task handler function."""
        self._manager._handle_task = handler

    def __repr__(self) -> str:
        return f"JobManager(project_path='{self.project_path}')"