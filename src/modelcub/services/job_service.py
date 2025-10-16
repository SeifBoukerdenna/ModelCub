"""
Job service - CLI handlers for annotation job management.
"""
import time
from pathlib import Path
from typing import Optional

from .annotation_job_manager import (
    AnnotationJobManager,
    JobStatus
)
from ..core.paths import project_root


def create_job(args) -> int:
    """Create a new annotation job."""
    try:
        root = project_root()
        manager = AnnotationJobManager(root, num_workers=args.workers)

        image_list = list(args.images) if args.images else None
        job = manager.create_job(args.dataset, image_list)

        print(f"✓ Created job {job.job_id}")
        print(f"  Dataset: {job.dataset_name}")
        print(f"  Tasks: {job.total_tasks}")

        if args.auto_start:
            print()
            job = manager.start_job(job.job_id)
            print(f"▶ Started job {job.job_id}")

            if hasattr(args, 'watch') and args.watch:
                return _watch_job(manager, job.job_id)
        else:
            print(f"\nStart with: modelcub job start {job.job_id}")

        return 0

    except Exception as e:
        print(f"❌ {e}")
        return 1


def start_job(args) -> int:
    """Start or resume a job."""
    try:
        root = project_root()
        manager = AnnotationJobManager(root)

        job = manager.start_job(args.job_id)
        print(f"▶ Started job {job.job_id}")
        print(f"  Status: {job.status.value}")
        print(f"  Progress: {job.progress:.1f}%")

        if args.watch:
            return _watch_job(manager, args.job_id)
        else:
            print(f"\nWatch progress: modelcub job watch {args.job_id}")

        return 0

    except Exception as e:
        print(f"❌ {e}")
        return 1


def pause_job(args) -> int:
    """Pause a running job."""
    try:
        root = project_root()
        manager = AnnotationJobManager(root)

        job = manager.pause_job(args.job_id)
        print(f"⏸ Paused job {job.job_id}")
        print(f"  Progress: {job.completed_tasks}/{job.total_tasks} ({job.progress:.1f}%)")
        print(f"\nResume with: modelcub job start {job.job_id}")

        return 0

    except Exception as e:
        print(f"❌ {e}")
        return 1


def cancel_job(args) -> int:
    """Cancel a job."""
    try:
        if not args.force:
            confirm = input(f"Cancel job {args.job_id}? [y/N]: ")
            if confirm.lower() not in ('y', 'yes'):
                print("❌ Cancelled")
                return 1

        root = project_root()
        manager = AnnotationJobManager(root)

        job = manager.cancel_job(args.job_id)
        print(f"✖ Cancelled job {job.job_id}")

        return 0

    except Exception as e:
        print(f"❌ {e}")
        return 1


def list_jobs(args) -> int:
    """List all jobs."""
    try:
        root = project_root()
        manager = AnnotationJobManager(root)

        status_filter = JobStatus(args.status) if args.status else None
        jobs = manager.list_jobs(status_filter)

        if not jobs:
            print("No jobs found")
            return 0

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

        print()
        return 0

    except Exception as e:
        print(f"❌ {e}")
        return 1


def get_job_status(args) -> int:
    """Get detailed job status."""
    try:
        root = project_root()
        manager = AnnotationJobManager(root)

        job = manager.get_job(args.job_id)
        if not job:
            print(f"❌ Job not found: {args.job_id}")
            return 1

        print(f"\n{'='*60}")
        print(f"Job {job.job_id}")
        print(f"{'='*60}")
        print(f"Dataset:    {job.dataset_name}")
        print(f"Status:     {job.status.value}")
        print(f"Progress:   {job.completed_tasks}/{job.total_tasks} ({job.progress:.1f}%)")

        if job.failed_tasks > 0:
            print(f"Failed:     {job.failed_tasks}")

        print(f"Created:    {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if job.started_at:
            print(f"Started:    {job.started_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if job.completed_at:
            print(f"Completed:  {job.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")

            if job.started_at:
                duration = (job.completed_at - job.started_at).total_seconds()
                print(f"Duration:   {duration:.1f}s")

        if job.error_message:
            print(f"\n⚠️  Error: {job.error_message}")

        print(f"{'='*60}\n")

        return 0

    except Exception as e:
        print(f"❌ {e}")
        return 1


def watch_job(args) -> int:
    """Watch job progress."""
    try:
        root = project_root()
        manager = AnnotationJobManager(root)

        return _watch_job(manager, args.job_id)

    except Exception as e:
        print(f"❌ {e}")
        return 1


def _watch_job(manager: AnnotationJobManager, job_id: str) -> int:
    """Internal function to watch job progress with live updates."""
    print(f"\nWatching job {job_id} (Ctrl+C to stop watching)\n")

    try:
        last_progress = -1

        while True:
            job = manager.get_job(job_id)
            if not job:
                print(f"\n❌ Job not found: {job_id}")
                return 1

            if job.progress != last_progress:
                progress_bar = _create_progress_bar(job.progress, width=40)
                status_icon = {
                    JobStatus.PENDING: "⏳",
                    JobStatus.RUNNING: "▶",
                    JobStatus.PAUSED: "⏸",
                    JobStatus.COMPLETED: "✓",
                    JobStatus.FAILED: "✖",
                    JobStatus.CANCELLED: "⊗"
                }.get(job.status, "?")

                print(f"\r{status_icon} {progress_bar} {job.progress:5.1f}% ({job.completed_tasks}/{job.total_tasks})",
                      end='', flush=True)
                last_progress = job.progress

            if job.is_terminal:
                print()

                if job.status == JobStatus.COMPLETED:
                    print(f"\n✓ Job completed successfully!")
                    if job.started_at and job.completed_at:
                        duration = (job.completed_at - job.started_at).total_seconds()
                        print(f"  Duration: {duration:.1f}s")
                        if duration > 0:
                            rate = job.total_tasks / duration
                            print(f"  Rate: {rate:.1f} tasks/sec")
                    return 0

                elif job.status == JobStatus.FAILED:
                    print(f"\n✖ Job failed")
                    if job.error_message:
                        print(f"  Error: {job.error_message}")
                    return 1

                elif job.status == JobStatus.CANCELLED:
                    print(f"\n⊗ Job cancelled")
                    return 0

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\n⏸ Stopped watching (job still running in background)")
        print(f"Check status: modelcub job status {job_id}")
        return 0


def _create_progress_bar(progress: float, width: int = 40) -> str:
    """Create a text-based progress bar."""
    filled = int(width * progress / 100)
    empty = width - filled
    return f"[{'█' * filled}{'░' * empty}]"