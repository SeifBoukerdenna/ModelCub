"""Annotation job management commands."""
import click


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
    from modelcub.services.job_service import create_job
    import argparse

    # Create argparse-like namespace for compatibility
    args = argparse.Namespace(
        dataset=dataset,
        images=list(images) if images else None,
        workers=workers,
        auto_start=auto_start
    )

    code = create_job(args)
    raise SystemExit(code)


@job.command()
@click.argument('job_id')
@click.option('--watch', is_flag=True, help='Watch job progress')
def start(job_id: str, watch: bool):
    """Start or resume a job."""
    from modelcub.services.job_service import start_job
    import argparse

    args = argparse.Namespace(
        job_id=job_id,
        watch=watch
    )

    code = start_job(args)
    raise SystemExit(code)


@job.command()
@click.argument('job_id')
def pause(job_id: str):
    """Pause a running job."""
    from modelcub.services.job_service import pause_job
    import argparse

    args = argparse.Namespace(job_id=job_id)
    code = pause_job(args)
    raise SystemExit(code)


@job.command()
@click.argument('job_id')
@click.option('--force', is_flag=True, help='Skip confirmation')
def cancel(job_id: str, force: bool):
    """Cancel a job."""
    from modelcub.services.job_service import cancel_job
    import argparse

    args = argparse.Namespace(
        job_id=job_id,
        force=force
    )

    code = cancel_job(args)
    raise SystemExit(code)


@job.command(name='list')
@click.option('--status',
              type=click.Choice(['pending', 'running', 'paused', 'completed', 'failed', 'cancelled']),
              help='Filter by status')
def list_jobs(status: str):
    """List all jobs."""
    from modelcub.services.job_service import list_jobs
    import argparse

    args = argparse.Namespace(status=status)
    code = list_jobs(args)
    raise SystemExit(code)


@job.command()
@click.argument('job_id')
def status(job_id: str):
    """Get detailed job status."""
    from modelcub.services.job_service import get_job_status
    import argparse

    args = argparse.Namespace(job_id=job_id)
    code = get_job_status(args)
    raise SystemExit(code)


@job.command()
@click.argument('job_id')
def watch(job_id: str):
    """Watch job progress."""
    from modelcub.services.job_service import watch_job
    import argparse

    args = argparse.Namespace(job_id=job_id)
    code = watch_job(args)
    raise SystemExit(code)