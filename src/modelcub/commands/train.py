"""Training management commands."""
import click
import time
from pathlib import Path


@click.group()
def train():
    """Manage training runs."""
    pass


@train.command()
@click.argument('dataset_name')
@click.option('--model', default='yolov8n', help='Model architecture (e.g., yolov8n, yolov8s)')
@click.option('--epochs', default=100, type=int, help='Number of training epochs')
@click.option('--imgsz', default=640, type=int, help='Input image size')
@click.option('--batch', default=16, type=int, help='Batch size')
@click.option('--device', default='auto', help='Device (auto, cpu, cuda, cuda:0)')
@click.option('--patience', default=50, type=int, help='Early stopping patience')
@click.option('--save-period', default=10, type=int, help='Save checkpoint every N epochs')
@click.option('--workers', default=8, type=int, help='Number of data loading workers')
@click.option('--seed', type=int, help='Random seed for reproducibility')
@click.option('--task', default='detect', type=click.Choice(['detect', 'segment', 'classify']),
              help='Task type')
def create(dataset_name: str, model: str, epochs: int, imgsz: int, batch: int,
           device: str, patience: int, save_period: int, workers: int, seed: int, task: str):
    """
    Create a new training run.

    Examples:
        modelcub train create my-dataset
        modelcub train create my-dataset --model yolov8s --epochs 50
        modelcub train create my-dataset --device cuda:0 --batch 32
    """
    from modelcub.services.training.training_service import TrainingService
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        service = TrainingService(root)

        click.echo(f"🎯 Creating training run...")
        click.echo(f"   Dataset: {dataset_name}")
        click.echo(f"   Model: {model}")
        click.echo(f"   Epochs: {epochs}")
        click.echo(f"   Device: {device}")
        click.echo()

        # Prepare kwargs
        kwargs = {}
        if seed is not None:
            kwargs['seed'] = seed

        # Create run
        run_id = service.create_run(
            dataset_name=dataset_name,
            model=model,
            epochs=epochs,
            task=task,
            imgsz=imgsz,
            batch=batch,
            device=device,
            patience=patience,
            save_period=save_period,
            workers=workers,
            **kwargs
        )

        click.echo(f"✅ Created training run: {run_id}")
        click.echo(f"\nNext steps:")
        click.echo(f"  • Start training:  modelcub train start {run_id}")
        click.echo(f"  • Check status:    modelcub train status {run_id}")

    except ValueError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Failed to create training run: {e}")
        raise SystemExit(2)


@train.command()
@click.argument('run_id')
@click.option('--watch', '-w', is_flag=True, help='Watch training logs in real-time')
def start(run_id: str, watch: bool):
    """
    Start a pending training run.

    Examples:
        modelcub train start run-20251027-143022
        modelcub train start run-20251027-143022 --watch
    """
    from modelcub.services.training.training_service import TrainingService
    from modelcub.core.paths import project_root
    import time

    try:
        root = project_root()
        service = TrainingService(root)

        click.echo(f"🚀 Starting training run: {run_id}")
        click.echo()

        service.start_run(run_id)

        click.echo(f"✅ Training started!")

        if not watch:
            click.echo(f"\nMonitor progress:")
            click.echo(f"  • Check status:  modelcub train status {run_id}")
            click.echo(f"  • View logs:     modelcub train logs {run_id} --follow")
            click.echo(f"  • Stop training: modelcub train stop {run_id}")
            return

        # Watch mode - tail logs
        click.echo(f"\n📜 Following training logs (Ctrl+C to stop)...")
        click.echo(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        # Get run info for log path
        run = service.get_status(run_id)
        run_path = root / run['artifacts_path']
        log_file = run_path / 'logs' / 'stdout.log'

        # Wait for log file to be created
        max_wait = 10
        waited = 0
        while not log_file.exists() and waited < max_wait:
            time.sleep(0.5)
            waited += 0.5

        if not log_file.exists():
            click.echo(f"⚠️  Log file not created yet. Run:")
            click.echo(f"   modelcub train logs {run_id} --follow")
            return

        try:
            with open(log_file, 'r') as f:
                # Start from beginning
                f.seek(0)

                # Stream new lines
                while True:
                    line = f.readline()
                    if line:
                        click.echo(line, nl=False)
                    else:
                        # No new data, check if process still running
                        time.sleep(0.5)
                        current_run = service.get_status(run_id)
                        if current_run['status'] not in ['running', 'pending']:
                            # Training finished, show final lines
                            for line in f:
                                click.echo(line, nl=False)
                            click.echo(f"\n\n✅ Training finished with status: {current_run['status']}")
                            break

        except KeyboardInterrupt:
            click.echo(f"\n\n👋 Stopped watching logs")
            click.echo(f"\nTraining is still running in background.")
            click.echo(f"  • Check status: modelcub train status {run_id}")
            click.echo(f"  • View logs:    modelcub train logs {run_id} --follow")
            click.echo(f"  • Stop:         modelcub train stop {run_id}")

    except ValueError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Failed to start training: {e}")
        raise SystemExit(2)


@train.command()
@click.argument('run_id')
@click.option('--timeout', default=10.0, type=float, help='Seconds to wait for graceful shutdown')
def stop(run_id: str, timeout: float):
    """
    Stop a running training run.

    Examples:
        modelcub train stop run-20251027-143022
        modelcub train stop run-20251027-143022 --timeout 30
    """
    from modelcub.services.training.training_service import TrainingService
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        service = TrainingService(root)

        click.echo(f"🛑 Stopping training run: {run_id}")
        click.echo(f"   Timeout: {timeout}s")
        click.echo()

        service.stop_run(run_id, timeout=timeout)

        click.echo(f"✅ Training stopped successfully")

    except ValueError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Failed to stop training: {e}")
        raise SystemExit(2)


@train.command()
@click.argument('run_id')
@click.option('--watch', '-w', is_flag=True, help='Watch and auto-refresh every 5 seconds')
def status(run_id: str, watch: bool):
    """
    Get status of a training run.

    Examples:
        modelcub train status run-20251027-143022
        modelcub train status run-20251027-143022 --watch
    """
    from modelcub.services.training.training_service import TrainingService
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        service = TrainingService(root)

        def show_status():
            run = service.get_status(run_id)

            click.echo(f"📊 Training Run: {run_id}")
            click.echo(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            click.echo(f"Status:        {_colorize_status(run['status'])}")
            click.echo(f"Dataset:       {run['dataset_name']}")
            click.echo(f"Model:         {run['config']['model']}")
            click.echo(f"Task:          {run['task']}")
            click.echo(f"Created:       {run['created']}")

            if run['status'] == 'running':
                click.echo(f"PID:           {run.get('pid', 'N/A')}")
                if 'started' in run:
                    click.echo(f"Started:       {run['started']}")

            if run['status'] == 'completed':
                click.echo()
                click.echo(f"📈 Results:")
                metrics = run.get('metrics', {})
                if metrics:
                    click.echo(f"   mAP50:      {metrics.get('map50', 'N/A')}")
                    click.echo(f"   mAP50-95:   {metrics.get('map50_95', 'N/A')}")
                    click.echo(f"   Precision:  {metrics.get('precision', 'N/A')}")
                    click.echo(f"   Recall:     {metrics.get('recall', 'N/A')}")
                    if 'best_epoch' in metrics:
                        click.echo(f"   Best Epoch: {metrics['best_epoch']}")

                if run.get('duration_ms'):
                    duration_sec = run['duration_ms'] / 1000
                    click.echo(f"\n⏱️  Duration: {_format_duration(duration_sec)}")

            if run['status'] == 'failed':
                click.echo()
                click.echo(f"❌ Error: {run.get('error', 'Unknown error')}")

            click.echo(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            # Config summary
            config = run['config']
            click.echo(f"\n⚙️  Configuration:")
            click.echo(f"   Epochs:     {config['epochs']}")
            click.echo(f"   Batch:      {config['batch']}")
            click.echo(f"   Image Size: {config['imgsz']}")
            click.echo(f"   Device:     {config['device']}")
            click.echo(f"   Patience:   {config['patience']}")

            # Artifacts
            click.echo(f"\n📁 Artifacts:")
            click.echo(f"   {run['artifacts_path']}")

        if watch:
            try:
                while True:
                    click.clear()
                    show_status()
                    run = service.get_status(run_id)
                    if run['status'] not in ['pending', 'running']:
                        click.echo(f"\n✅ Training finished with status: {run['status']}")
                        break
                    click.echo(f"\n♻️  Refreshing in 5s... (Ctrl+C to stop)")
                    time.sleep(5)
            except KeyboardInterrupt:
                click.echo(f"\n\n👋 Stopped watching")
        else:
            show_status()

    except ValueError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Failed to get status: {e}")
        raise SystemExit(2)


@train.command(name='list')
@click.option('--status', type=click.Choice(['pending', 'running', 'completed', 'failed', 'cancelled']),
              help='Filter by status')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def list_runs(status: str, output_json: bool):
    """
    List all training runs.

    Examples:
        modelcub train list
        modelcub train list --status running
        modelcub train list --json
    """
    from modelcub.services.training.training_service import TrainingService
    from modelcub.core.paths import project_root
    import json

    try:
        root = project_root()
        service = TrainingService(root)

        runs = service.list_runs(status=status)

        if output_json:
            click.echo(json.dumps(runs, indent=2))
            return

        if not runs:
            click.echo("No training runs found.")
            return

        click.echo(f"\n📋 Training Runs ({len(runs)} total)")
        if status:
            click.echo(f"   Filtered by status: {status}")
        click.echo(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # Sort by created date (newest first)
        runs_sorted = sorted(runs, key=lambda r: r.get('created', ''), reverse=True)

        for run in runs_sorted:
            status_colored = _colorize_status(run['status'])
            click.echo(f"\n{run['id']}")
            click.echo(f"  Status:  {status_colored}")
            click.echo(f"  Dataset: {run['dataset_name']}")
            click.echo(f"  Model:   {run['config']['model']}")
            click.echo(f"  Created: {run['created']}")

            if run['status'] == 'completed' and run.get('metrics'):
                metrics = run['metrics']
                click.echo(f"  mAP50:   {metrics.get('map50', 'N/A')}")

            if run['status'] == 'failed' and run.get('error'):
                click.echo(f"  Error:   {run['error'][:60]}...")

        click.echo()

    except Exception as e:
        click.echo(f"❌ Failed to list runs: {e}")
        raise SystemExit(2)


@train.command()
@click.argument('run_id')
@click.option('--yes', '-y', is_flag=True, help='Confirm deletion without prompting')
@click.option('--keep-artifacts', is_flag=True, help='Keep artifacts directory (only remove from registry)')
def delete(run_id: str, yes: bool, keep_artifacts: bool):
    """
    Delete a training run.

    Removes run from registry and optionally deletes artifacts.

    Examples:
        modelcub train delete run-20251027-143022
        modelcub train delete run-20251027-143022 --yes
        modelcub train delete run-20251027-143022 --keep-artifacts
    """
    from modelcub.services.training.training_service import TrainingService
    from modelcub.core.paths import project_root
    import shutil

    try:
        root = project_root()
        service = TrainingService(root)

        # Get run info
        run = service.get_status(run_id)

        # Don't delete running runs
        if run['status'] == 'running':
            click.echo(f"❌ Cannot delete running run. Stop it first:")
            click.echo(f"   modelcub train stop {run_id}")
            raise SystemExit(2)

        # Confirm deletion
        if not yes:
            click.echo(f"⚠️  About to delete run: {run_id}")
            click.echo(f"   Status:  {run['status']}")
            click.echo(f"   Dataset: {run['dataset_name']}")
            click.echo(f"   Model:   {run['config']['model']}")

            if not keep_artifacts:
                click.echo(f"   ⚠️  Will also delete artifacts: {run['artifacts_path']}")

            click.echo()
            if not click.confirm("Are you sure?"):
                click.echo("Cancelled.")
                return

        # Delete artifacts if requested
        if not keep_artifacts:
            artifacts_path = root / run['artifacts_path']
            if artifacts_path.exists():
                shutil.rmtree(artifacts_path)
                click.echo(f"🗑️  Deleted artifacts: {run['artifacts_path']}")

        # Remove from registry
        service.run_registry.remove_run(run_id)

        click.echo(f"✅ Run deleted: {run_id}")

    except ValueError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Failed to delete run: {e}")
        raise SystemExit(2)


@train.command()
@click.argument('run_id')
@click.option('--force', '-f', is_flag=True, help='Force restart even if not failed/cancelled')
def restart(run_id: str, force: bool):
    """
    Restart a failed or cancelled training run.

    Stops the run if running, resets to pending, and starts again.

    Examples:
        modelcub train restart run-20251027-143022
        modelcub train restart run-20251027-143022 --force
    """
    from modelcub.services.training.training_service import TrainingService
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        service = TrainingService(root)

        # Get run info
        run = service.get_status(run_id)

        # Check if restart is allowed
        if not force and run['status'] not in ['failed', 'cancelled']:
            click.echo(f"❌ Can only restart failed or cancelled runs (current: {run['status']})")
            click.echo(f"   Use --force to restart anyway")
            raise SystemExit(2)

        click.echo(f"🔄 Restarting run: {run_id}")
        click.echo(f"   Previous status: {run['status']}")

        # Stop if running
        if run['status'] == 'running':
            click.echo(f"   Stopping current process...")
            service.stop_run(run_id)

        # Reset to pending
        service.run_registry.update_run(run_id, {
            'status': 'pending',
            'pid': None,
            'error': None,
            'started': None,
            'duration_ms': None,
            'metrics': {}
        })

        click.echo(f"   Reset to pending")
        click.echo()

        # Start training
        service.start_run(run_id)

        click.echo(f"✅ Training restarted!")
        click.echo(f"\nMonitor progress:")
        click.echo(f"  • Check status:  modelcub train status {run_id}")
        click.echo(f"  • View logs:     modelcub train logs {run_id} --follow")

    except ValueError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Failed to restart run: {e}")
        raise SystemExit(2)


@train.command()
@click.argument('run_id')
@click.option('--follow', '-f', is_flag=True, help='Follow log output (tail -f style)')
@click.option('--stderr', is_flag=True, help='Show stderr instead of stdout')
@click.option('--lines', '-n', type=int, default=50, help='Number of lines to show')
def logs(run_id: str, follow: bool, stderr: bool, lines: int):
    """
    View training logs.

    Examples:
        modelcub train logs run-20251027-143022
        modelcub train logs run-20251027-143022 --follow
        modelcub train logs run-20251027-143022 --stderr
    """
    from modelcub.services.training.training_service import TrainingService
    from modelcub.core.paths import project_root

    try:
        root = project_root()
        service = TrainingService(root)

        # Get run info
        run = service.get_status(run_id)

        # Determine log file
        run_path = root / run['artifacts_path']
        log_type = 'stderr' if stderr else 'stdout'
        log_file = run_path / 'logs' / f'{log_type}.log'

        if not log_file.exists():
            click.echo(f"❌ Log file not found: {log_file}")
            raise SystemExit(2)

        if follow:
            # Follow mode - tail -f style
            click.echo(f"📜 Following {log_type} logs (Ctrl+C to stop)...")
            click.echo(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

            try:
                with open(log_file, 'r') as f:
                    # Show last N lines first
                    f.seek(0, 2)  # Go to end
                    file_size = f.tell()

                    # Read backwards to find last N lines
                    buffer_size = 4096
                    lines_found = []
                    block_end = file_size

                    while len(lines_found) < lines and block_end > 0:
                        block_start = max(0, block_end - buffer_size)
                        f.seek(block_start)
                        block = f.read(block_end - block_start)
                        lines_in_block = block.split('\n')
                        lines_found = lines_in_block + lines_found
                        block_end = block_start

                    # Show last N lines
                    for line in lines_found[-lines:]:
                        if line:
                            click.echo(line)

                    # Now follow new lines
                    while True:
                        line = f.readline()
                        if line:
                            click.echo(line, nl=False)
                        else:
                            time.sleep(0.5)
                            # Check if run finished
                            current_run = service.get_status(run_id)
                            if current_run['status'] not in ['running', 'pending']:
                                click.echo(f"\n\n✅ Training finished with status: {current_run['status']}")
                                break

            except KeyboardInterrupt:
                click.echo(f"\n\n👋 Stopped following logs")

        else:
            # Static mode - show last N lines
            click.echo(f"📜 Last {lines} lines of {log_type}")
            click.echo(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    click.echo(line, nl=False)

    except ValueError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Failed to read logs: {e}")
        raise SystemExit(2)


def _colorize_status(status: str) -> str:
    """Add color to status display."""
    colors = {
        'pending': ('yellow', '⏳'),
        'running': ('blue', '▶️'),
        'completed': ('green', '✅'),
        'failed': ('red', '❌'),
        'cancelled': ('magenta', '⚠️')
    }

    color, emoji = colors.get(status, ('white', '•'))
    return click.style(f"{emoji} {status}", fg=color, bold=True)


def _format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"