"""
Robust annotation job management system with resume, pause, cancel capabilities.
Integrates with existing ModelCub annotation service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
import json
import sqlite3
import threading
import time
from queue import Queue, Empty
import uuid


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AnnotationTask:
    """Single annotation task (one image)"""
    task_id: str
    job_id: str
    image_id: str
    image_path: str
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None


@dataclass
class AnnotationJob:
    """Annotation job containing multiple tasks"""
    job_id: str
    dataset_name: str
    project_path: Path
    status: JobStatus = JobStatus.PENDING
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    error_message: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)

    @property
    def progress(self) -> float:
        """Progress percentage"""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100

    @property
    def is_terminal(self) -> bool:
        """Check if job is in terminal state"""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]

    @property
    def can_resume(self) -> bool:
        """Check if job can be resumed"""
        return self.status in [JobStatus.PAUSED, JobStatus.FAILED]


class JobStore:
    """Persistent storage for jobs and tasks using SQLite"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    dataset_name TEXT NOT NULL,
                    project_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    total_tasks INTEGER DEFAULT 0,
                    completed_tasks INTEGER DEFAULT 0,
                    failed_tasks INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    paused_at TEXT,
                    error_message TEXT,
                    config TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    image_id TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER DEFAULT 0,
                    error_message TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    result TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs (job_id)
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_job_id ON tasks(job_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)")
            conn.commit()

    def save_job(self, job: AnnotationJob):
        """Save or update job"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO jobs
                (job_id, dataset_name, project_path, status, total_tasks,
                 completed_tasks, failed_tasks, created_at, started_at,
                 completed_at, paused_at, error_message, config)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.job_id,
                job.dataset_name,
                str(job.project_path),
                job.status.value,
                job.total_tasks,
                job.completed_tasks,
                job.failed_tasks,
                job.created_at.isoformat(),
                job.started_at.isoformat() if job.started_at else None,
                job.completed_at.isoformat() if job.completed_at else None,
                job.paused_at.isoformat() if job.paused_at else None,
                job.error_message,
                json.dumps(job.config)
            ))
            conn.commit()

    def load_job(self, job_id: str) -> Optional[AnnotationJob]:
        """Load job from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return AnnotationJob(
                job_id=row['job_id'],
                dataset_name=row['dataset_name'],
                project_path=Path(row['project_path']),
                status=JobStatus(row['status']),
                total_tasks=row['total_tasks'],
                completed_tasks=row['completed_tasks'],
                failed_tasks=row['failed_tasks'],
                created_at=datetime.fromisoformat(row['created_at']),
                started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
                completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                paused_at=datetime.fromisoformat(row['paused_at']) if row['paused_at'] else None,
                error_message=row['error_message'],
                config=json.loads(row['config']) if row['config'] else {}
            )

    def save_task(self, task: AnnotationTask):
        """Save or update task"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks
                (task_id, job_id, image_id, image_path, status, attempts,
                 error_message, started_at, completed_at, result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id,
                task.job_id,
                task.image_id,
                task.image_path,
                task.status.value,
                task.attempts,
                task.error_message,
                task.started_at.isoformat() if task.started_at else None,
                task.completed_at.isoformat() if task.completed_at else None,
                json.dumps(task.result) if task.result else None
            ))
            conn.commit()

    def load_tasks(self, job_id: str, status: Optional[TaskStatus] = None) -> List[AnnotationTask]:
        """Load tasks for a job"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if status:
                cursor = conn.execute(
                    "SELECT * FROM tasks WHERE job_id = ? AND status = ?",
                    (job_id, status.value)
                )
            else:
                cursor = conn.execute("SELECT * FROM tasks WHERE job_id = ?", (job_id,))

            tasks = []
            for row in cursor.fetchall():
                tasks.append(AnnotationTask(
                    task_id=row['task_id'],
                    job_id=row['job_id'],
                    image_id=row['image_id'],
                    image_path=row['image_path'],
                    status=TaskStatus(row['status']),
                    attempts=row['attempts'],
                    error_message=row['error_message'],
                    started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
                    completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                    result=json.loads(row['result']) if row['result'] else None
                ))

            return tasks

    def list_jobs(self, status: Optional[JobStatus] = None) -> List[AnnotationJob]:
        """List all jobs, optionally filtered by status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if status:
                cursor = conn.execute("SELECT * FROM jobs WHERE status = ?", (status.value,))
            else:
                cursor = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC")

            jobs = []
            for row in cursor.fetchall():
                jobs.append(AnnotationJob(
                    job_id=row['job_id'],
                    dataset_name=row['dataset_name'],
                    project_path=Path(row['project_path']),
                    status=JobStatus(row['status']),
                    total_tasks=row['total_tasks'],
                    completed_tasks=row['completed_tasks'],
                    failed_tasks=row['failed_tasks'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
                    completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
                    paused_at=datetime.fromisoformat(row['paused_at']) if row['paused_at'] else None,
                    error_message=row['error_message'],
                    config=json.loads(row['config']) if row['config'] else {}
                ))

            return jobs


class JobWorker(threading.Thread):
    """Worker thread that processes annotation tasks"""

    def __init__(
        self,
        worker_id: int,
        task_queue: Queue,
        store: JobStore,
        task_handler: Callable[[AnnotationTask], Dict[str, Any]],
        max_retries: int = 3
    ):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.store = store
        self.task_handler = task_handler
        self.max_retries = max_retries
        self._stop_event = threading.Event()

    def stop(self):
        """Signal worker to stop"""
        self._stop_event.set()

    def run(self):
        """Worker main loop"""
        while not self._stop_event.is_set():
            try:
                task = self.task_queue.get(timeout=0.5)
            except Empty:
                continue

            try:
                # Mark task as in progress
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.now()
                task.attempts += 1
                self.store.save_task(task)

                # Execute task
                result = self.task_handler(task)

                # Mark as completed
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = result
                self.store.save_task(task)

            except Exception as e:
                # Handle failure
                task.error_message = str(e)

                if task.attempts >= self.max_retries:
                    task.status = TaskStatus.FAILED
                else:
                    # Retry - put back in queue
                    task.status = TaskStatus.PENDING
                    self.task_queue.put(task)

                self.store.save_task(task)

            finally:
                self.task_queue.task_done()


class AnnotationJobManager:
    """
    Central manager for annotation jobs with resume/pause/cancel capabilities.

    Features:
    - Create jobs from datasets
    - Start, pause, resume, cancel jobs
    - Automatic checkpointing and recovery
    - Multi-threaded task execution
    - Progress tracking
    - Event notifications
    """

    def __init__(
        self,
        project_path: Path,
        num_workers: int = 4,
        max_retries: int = 3
    ):
        self.project_path = project_path
        self.num_workers = num_workers
        self.max_retries = max_retries

        # Initialize storage
        db_path = project_path / ".modelcub" / "jobs.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.store = JobStore(db_path)

        # Worker management
        self.task_queue: Queue = Queue()
        self.workers: List[JobWorker] = []
        self.active_jobs: Dict[str, AnnotationJob] = {}
        self._lock = threading.Lock()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def create_job(
        self,
        dataset_name: str,
        image_ids: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> AnnotationJob:
        """
        Create a new annotation job.

        Args:
            dataset_name: Dataset to annotate
            image_ids: Specific images to annotate (or None for all)
            config: Job configuration

        Returns:
            Created job
        """
        from modelcub.services.annotation_service import get_annotation, GetAnnotationRequest

        job_id = str(uuid.uuid4())[:8]

        # Get dataset images
        req = GetAnnotationRequest(
            dataset_name=dataset_name,
            image_id=None,
            project_path=self.project_path
        )

        code, result = get_annotation(req)
        if code != 0:
            raise ValueError(f"Failed to get dataset images: {result}")

        data = json.loads(result)
        all_images = data.get("images", [])

        # Filter images if specified
        if image_ids:
            images = [img for img in all_images if img["image_id"] in image_ids]
        else:
            images = all_images

        # Create job
        job = AnnotationJob(
            job_id=job_id,
            dataset_name=dataset_name,
            project_path=self.project_path,
            total_tasks=len(images),
            config=config or {}
        )

        # Create tasks
        tasks = []
        for img in images:
            task = AnnotationTask(
                task_id=f"{job_id}_{img['image_id']}",
                job_id=job_id,
                image_id=img["image_id"],
                image_path=img["image_path"]
            )
            tasks.append(task)

        # Save to database
        self.store.save_job(job)
        for task in tasks:
            self.store.save_task(task)

        return job

    def start_job(self, job_id: str) -> AnnotationJob:
        """Start or resume a job"""
        job = self.store.load_job(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        if job.status == JobStatus.RUNNING:
            return job  # Already running

        if not job.can_resume and job.status != JobStatus.PENDING:
            raise ValueError(f"Cannot start job in status: {job.status}")

        # Update job status
        job.status = JobStatus.RUNNING
        job.started_at = job.started_at or datetime.now()
        job.paused_at = None
        self.store.save_job(job)

        # Load pending tasks
        pending_tasks = self.store.load_tasks(job_id, TaskStatus.PENDING)

        # Enqueue tasks
        for task in pending_tasks:
            self.task_queue.put(task)

        # Start workers if not already running
        self._ensure_workers_running()

        # Start monitoring thread
        if not self._monitor_thread or not self._monitor_thread.is_alive():
            self._monitor_thread = threading.Thread(
                target=self._monitor_jobs,
                daemon=True
            )
            self._monitor_thread.start()

        with self._lock:
            self.active_jobs[job_id] = job

        return job

    def pause_job(self, job_id: str) -> AnnotationJob:
        """Pause a running job"""
        job = self.store.load_job(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        if job.status != JobStatus.RUNNING:
            raise ValueError(f"Cannot pause job in status: {job.status}")

        # Update status
        job.status = JobStatus.PAUSED
        job.paused_at = datetime.now()
        self.store.save_job(job)

        with self._lock:
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]

        return job

    def cancel_job(self, job_id: str) -> AnnotationJob:
        """Cancel a job"""
        job = self.store.load_job(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")

        if job.is_terminal:
            return job  # Already in terminal state

        # Update status
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now()
        self.store.save_job(job)

        # Mark pending tasks as skipped
        pending_tasks = self.store.load_tasks(job_id, TaskStatus.PENDING)
        for task in pending_tasks:
            task.status = TaskStatus.SKIPPED
            self.store.save_task(task)

        with self._lock:
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]

        return job

    def get_job(self, job_id: str) -> Optional[AnnotationJob]:
        """Get job status"""
        return self.store.load_job(job_id)

    def list_jobs(self, status: Optional[JobStatus] = None) -> List[AnnotationJob]:
        """List all jobs"""
        return self.store.list_jobs(status)

    def get_tasks(self, job_id: str, status: Optional[TaskStatus] = None) -> List[AnnotationTask]:
        """Get tasks for a job"""
        return self.store.load_tasks(job_id, status)

    def _ensure_workers_running(self):
        """Ensure worker threads are running"""
        # Clean up dead workers
        self.workers = [w for w in self.workers if w.is_alive()]

        # Start new workers if needed
        while len(self.workers) < self.num_workers:
            worker = JobWorker(
                worker_id=len(self.workers),
                task_queue=self.task_queue,
                store=self.store,
                task_handler=self._handle_task,
                max_retries=self.max_retries
            )
            worker.start()
            self.workers.append(worker)

    def _handle_task(self, task: AnnotationTask) -> Dict[str, Any]:
        """
        Handle a single annotation task.
        This should be customized based on your annotation logic.
        """
        # Example: Auto-annotate using a model, or validate existing annotations
        # For now, just a placeholder that simulates work
        time.sleep(0.1)

        return {
            "processed": True,
            "timestamp": datetime.now().isoformat()
        }

    def _monitor_jobs(self):
        """Monitor active jobs and update their status"""
        while not self._stop_event.is_set():
            time.sleep(1)

            with self._lock:
                job_ids = list(self.active_jobs.keys())

            for job_id in job_ids:
                job = self.store.load_job(job_id)
                if not job:
                    continue

                # Count task statuses
                all_tasks = self.store.load_tasks(job_id)
                completed = sum(1 for t in all_tasks if t.status == TaskStatus.COMPLETED)
                failed = sum(1 for t in all_tasks if t.status == TaskStatus.FAILED)

                # Update job counters
                job.completed_tasks = completed
                job.failed_tasks = failed

                # Check if job is complete
                if completed + failed == job.total_tasks:
                    if failed == 0:
                        job.status = JobStatus.COMPLETED
                    else:
                        job.status = JobStatus.FAILED
                        job.error_message = f"{failed} tasks failed"

                    job.completed_at = datetime.now()

                    with self._lock:
                        if job_id in self.active_jobs:
                            del self.active_jobs[job_id]

                self.store.save_job(job)

    def shutdown(self):
        """Shutdown the job manager"""
        self._stop_event.set()

        # Stop workers
        for worker in self.workers:
            worker.stop()

        for worker in self.workers:
            worker.join(timeout=5)

        # Stop monitor
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)


# ============= CLI Integration =============

def cli_create_job(dataset_name: str, project_path: Path, image_ids: Optional[List[str]] = None):
    """CLI: Create annotation job"""
    manager = AnnotationJobManager(project_path)
    job = manager.create_job(dataset_name, image_ids)

    print(f"✓ Created job {job.job_id}")
    print(f"  Dataset: {job.dataset_name}")
    print(f"  Tasks: {job.total_tasks}")
    print(f"\nRun: modelcub job start {job.job_id}")


def cli_start_job(job_id: str, project_path: Path):
    """CLI: Start job"""
    manager = AnnotationJobManager(project_path)
    job = manager.start_job(job_id)

    print(f"▶ Started job {job.job_id}")
    print(f"  Status: {job.status.value}")
    print(f"  Progress: {job.progress:.1f}%")


def cli_pause_job(job_id: str, project_path: Path):
    """CLI: Pause job"""
    manager = AnnotationJobManager(project_path)
    job = manager.pause_job(job_id)

    print(f"⏸ Paused job {job.job_id}")
    print(f"  Progress: {job.progress:.1f}%")


def cli_cancel_job(job_id: str, project_path: Path):
    """CLI: Cancel job"""
    manager = AnnotationJobManager(project_path)
    job = manager.cancel_job(job_id)

    print(f"✖ Cancelled job {job.job_id}")


def cli_list_jobs(project_path: Path):
    """CLI: List all jobs"""
    manager = AnnotationJobManager(project_path)
    jobs = manager.list_jobs()

    if not jobs:
        print("No jobs found")
        return

    print("\nAnnotation Jobs:")
    print("=" * 80)

    for job in jobs:
        status_icon = {
            JobStatus.PENDING: "⏳",
            JobStatus.RUNNING: "▶",
            JobStatus.PAUSED: "⏸",
            JobStatus.COMPLETED: "✓",
            JobStatus.FAILED: "✖",
            JobStatus.CANCELLED: "⊗"
        }.get(job.status, "?")

        print(f"\n{status_icon} {job.job_id} - {job.dataset_name}")
        print(f"   Status: {job.status.value}")
        print(f"   Progress: {job.completed_tasks}/{job.total_tasks} ({job.progress:.1f}%)")

        if job.failed_tasks > 0:
            print(f"   Failed: {job.failed_tasks}")

        print(f"   Created: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")