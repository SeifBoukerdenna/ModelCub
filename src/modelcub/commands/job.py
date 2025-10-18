"""Annotation job management commands."""
import click
from pathlib import Path


@click.group()
def job():
    """Manage annotation jobs."""
    pass


@job.command()
@click.argument('dataset')
@click.option('--images', multiple=True, help='Specific image IDs to annotate')
@click.option('--workers', type=int, default=4, help='Number of worker threads')
@click.option('--auto-start', is_flag=True, help='Automatically start the job')
def create(dataset: str, images: tuple, workers: int, auto_start: bool):
    """Create an annotation job."""
    from modelcub.services.annotation_job_manager import AnnotationJobManager
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        manager = AnnotationJobManager(root, num_workers=workers)

        image_list = list(images) if images else None
        job = manager.create_job(dataset, image_list)

        click.echo(f"✓ Created job {job.job_id}")
        click.echo(f"  Dataset: {job.dataset_name}")
        click.echo(f"  Tasks: {job.total_tasks}")

        if auto_start:
            job = manager.start_job(job.job_id)
            click.echo(f"▶ Started job {job.job_id}")
        else:
            click.echo(f"\nRun: modelcub job start {job.job_id}")

        raise SystemExit(0)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(2)


@job.command()
@click.argument('job_id')
@click.option('--watch', is_flag=True, help='Watch job progress')
def start(job_id: str, watch: bool):
    """Start or resume a job."""
    from modelcub.services.annotation_job_manager import AnnotationJobManager
    from modelcub.core.paths import project_root
    import time

    try:
        root = project_root()
        manager = AnnotationJobManager(root)
        job = manager.start_job(job_id)

        click.echo(f"▶ Started job {job.job_id}")
        click.echo(f"  Status: {job.status.value}")
        click.echo(f"  Progress: {job.progress:.1f}%")

        if watch:
            click.echo("\nWatching job progress (Ctrl+C to stop)...")
            try:
                while not job.is_terminal:
                    time.sleep(2)
                    job = manager.get_job(job_id)
                    click.echo(f"  Progress: {job.completed_tasks}/{job.total_tasks} ({job.progress:.1f}%)")

                click.echo(f"\n✓ Job completed with status: {job.status.value}")
            except KeyboardInterrupt:
                click.echo("\n\nStopped watching")

        raise SystemExit(0)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(2)


@job.command()
@click.argument('job_id')
def pause(job_id: str):
    """Pause a running job."""
    from modelcub.services.annotation_job_manager import AnnotationJobManager
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        manager = AnnotationJobManager(root)
        job = manager.pause_job(job_id)

        click.echo(f"⏸ Paused job {job.job_id}")
        click.echo(f"  Progress: {job.progress:.1f}%")
        raise SystemExit(0)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(2)


@job.command()
@click.argument('job_id')
@click.option('--force', is_flag=True, help='Skip confirmation')
def cancel(job_id: str, force: bool):
    """Cancel a job."""
    from modelcub.services.annotation_job_manager import AnnotationJobManager
    from modelcub.core.paths import project_root

    try:
        if not force:
            if not click.confirm(f"Cancel job {job_id}?"):
                click.echo("Cancelled")
                raise SystemExit(0)

        root = project_root()
        manager = AnnotationJobManager(root)
        job = manager.cancel_job(job_id)

        click.echo(f"✖ Cancelled job {job.job_id}")
        raise SystemExit(0)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(2)


@job.command(name='list')
@click.option('--status',
              type=click.Choice(['pending', 'running', 'paused', 'completed', 'failed', 'cancelled']),
              help='Filter by status')
def list_jobs(status: str):
    """List all jobs."""
    from modelcub.services.annotation_job_manager import AnnotationJobManager, JobStatus
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        manager = AnnotationJobManager(root)

        status_filter = JobStatus(status) if status else None
        jobs = manager.list_jobs(status_filter)

        if not jobs:
            click.echo("No jobs found")
            raise SystemExit(0)

        click.echo("\nAnnotation Jobs:")
        click.echo("=" * 80)

        for job in jobs:
            status_icon = {
                JobStatus.PENDING: "⏳",
                JobStatus.RUNNING: "▶",
                JobStatus.PAUSED: "⏸",
                JobStatus.COMPLETED: "✓",
                JobStatus.FAILED: "✖",
                JobStatus.CANCELLED: "⊗"
            }.get(job.status, "?")

            click.echo(f"\n{status_icon} {job.job_id} - {job.dataset_name}")
            click.echo(f"   Status: {job.status.value}")
            click.echo(f"   Progress: {job.completed_tasks}/{job.total_tasks} ({job.progress:.1f}%)")

            if job.failed_tasks > 0:
                click.echo(f"   Failed: {job.failed_tasks}")

            click.echo(f"   Created: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        raise SystemExit(0)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(2)


@job.command()
@click.argument('job_id')
def status(job_id: str):
    """Get detailed job status."""
    from modelcub.services.annotation_job_manager import AnnotationJobManager, TaskStatus
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        manager = AnnotationJobManager(root)
        job = manager.get_job(job_id)

        if not job:
            click.echo(f"❌ Job not found: {job_id}")
            raise SystemExit(2)

        click.echo(f"\n📋 Job {job.job_id}")
        click.echo("=" * 60)
        click.echo(f"Dataset: {job.dataset_name}")
        click.echo(f"Status: {job.status.value}")
        click.echo(f"Progress: {job.completed_tasks}/{job.total_tasks} ({job.progress:.1f}%)")

        if job.failed_tasks > 0:
            click.echo(f"Failed: {job.failed_tasks}")

        click.echo(f"\nCreated: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if job.started_at:
            click.echo(f"Started: {job.started_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if job.completed_at:
            click.echo(f"Completed: {job.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if job.paused_at:
            click.echo(f"Paused: {job.paused_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # Show task breakdown
        click.echo("\n📊 Task Status:")
        for task_status in TaskStatus:
            tasks = manager.get_tasks(job_id, task_status)
            if tasks:
                click.echo(f"  {task_status.value}: {len(tasks)}")

        raise SystemExit(0)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(2)


@job.command()
@click.argument('job_id')
def watch(job_id: str):
    """Watch job progress."""
    from modelcub.services.annotation_job_manager import AnnotationJobManager
    from modelcub.core.paths import project_root
    import time

    try:
        root = project_root()
        manager = AnnotationJobManager(root)
        job = manager.get_job(job_id)

        if not job:
            click.echo(f"❌ Job not found: {job_id}")
            raise SystemExit(2)

        click.echo(f"👀 Watching job {job.job_id} (Ctrl+C to stop)\n")

        try:
            while not job.is_terminal:
                click.echo(f"[{job.status.value}] Progress: {job.completed_tasks}/{job.total_tasks} ({job.progress:.1f}%)", nl=False)
                click.echo("\r", nl=False)
                time.sleep(2)
                job = manager.get_job(job_id)

            click.echo(f"\n\n✓ Job completed with status: {job.status.value}")

            if job.failed_tasks > 0:
                click.echo(f"⚠️  {job.failed_tasks} task(s) failed")

        except KeyboardInterrupt:
            click.echo("\n\nStopped watching")

        raise SystemExit(0)
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise SystemExit(2)