"""
Training service for managing model training lifecycle.

Orchestrates training runs, monitors progress, and manages results.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)


class TrainingService:
    """
    Core training service for ModelCub.

    Manages training run lifecycle: create, start, stop, monitor.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.runs_dir = project_root / "runs"

        # Import registries
        from ...core.registries import RunRegistry
        self.run_registry = RunRegistry(project_root)

        # Recover any orphaned processes on init
        self._recover_orphaned_processes()

    def create_run(
        self,
        dataset_name: str,
        model: str,
        epochs: int,
        task: str = "detect",
        imgsz: int = 640,
        batch: int = 16,
        device: str = "auto",
        patience: int = 50,
        save_period: int = 10,
        workers: int = 8,
        seed: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Create a new training run.

        Args:
            dataset_name: Name of dataset to train on
            model: Model architecture (e.g., "yolov8n")
            epochs: Number of training epochs
            task: Task type (detect, segment, classify)
            imgsz: Input image size
            batch: Batch size
            device: Device to train on (auto, cpu, cuda:0, etc.)
            patience: Early stopping patience
            save_period: Save checkpoint every N epochs
            workers: Number of data loading workers
            seed: Random seed for reproducibility
            **kwargs: Additional training parameters

        Returns:
            Run ID

        Raises:
            ValueError: If dataset doesn't exist or parameters are invalid
        """
        from .validation import validate_model_name, ValidationError
        from ...events.training import TrainingRunCreated
        from ...events.events import bus

        # Validate dataset exists
        from ...core.registries import DatasetRegistry
        dataset_registry = DatasetRegistry(self.project_root)
        if dataset_name not in [d['name'] for d in dataset_registry.list_datasets()]:
            raise ValueError(f"Dataset not found: {dataset_name}")

        # Validate model name
        try:
            validate_model_name(model)
        except ValidationError as e:
            raise ValueError(str(e))

        # Generate run ID
        run_id = self._generate_run_id()

        # Resolve device
        resolved_device = self._resolve_device(device)

        # Create snapshot
        from ...core.snapshots import create_snapshot, generate_snapshot_id, save_snapshot
        dataset_path = self.project_root / "data" / "datasets" / dataset_name
        snapshot_id = generate_snapshot_id()

        logger.info(f"Creating snapshot for dataset: {dataset_name}")
        snapshot = create_snapshot(dataset_path, dataset_name, snapshot_id)

        # Save snapshot
        snapshot_path = self.project_root / ".modelcub" / "snapshots" / f"{snapshot_id}.json"
        save_snapshot(snapshot, snapshot_path)

        # Prepare run configuration
        config = {
            'model': model,
            'epochs': epochs,
            'imgsz': imgsz,
            'batch': batch,
            'device': resolved_device,
            'patience': patience,
            'save_period': save_period,
            'workers': workers,
            'task': task
        }

        if seed is not None:
            config['seed'] = seed

        config.update(kwargs)

        # Create run directory
        run_path = self.runs_dir / run_id
        run_path.mkdir(parents=True, exist_ok=True)

        # Create run entry
        run_info = {
            'id': run_id,
            'created': datetime.utcnow().isoformat() + 'Z',
            'status': 'pending',
            'dataset_name': dataset_name,
            'dataset_snapshot_id': snapshot_id,
            'task': task,
            'config': config,
            'artifacts_path': str(run_path.relative_to(self.project_root)),
            'metrics': {},
            'pid': None,
            'duration_ms': None,
            'exit_code': None,
            'error': None
        }

        # Generate and save lockfile
        from ...core.lockfiles import generate_lockfile, save_lockfile
        lockfile = generate_lockfile(run_id, config, dataset_name, snapshot_id)
        lockfile_path = run_path / "config.lock.yaml"
        save_lockfile(lockfile, lockfile_path)

        # Add to registry
        self.run_registry.add_run(run_info)

        logger.info(f"Created training run: {run_id}")

        # Emit event
        bus.publish(TrainingRunCreated(
            run_id=run_id,
            dataset_name=dataset_name,
            model=model,
            epochs=epochs,
            device=resolved_device
        ))

        return run_id

    def start_run(self, run_id: str) -> None:
        """
        Start a pending training run.

        Args:
            run_id: Run identifier

        Raises:
            ValueError: If run doesn't exist or is not in pending state
            RuntimeError: If training process fails to start
        """
        from .validation import validate_all, ValidationError
        from ...events.training import TrainingStarted, TrainingFailed
        from ...events.events import bus

        # Get run info
        run = self.run_registry.get_run(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")

        if run['status'] != 'pending':
            raise ValueError(f"Run {run_id} is not pending (status: {run['status']})")

        # Get dataset path
        dataset_path = self.project_root / "data" / "datasets" / run['dataset_name']

        # Validate before starting
        try:
            logger.info(f"Validating run {run_id}")
            validate_all(
                dataset_path=dataset_path,
                model=run['config']['model'],
                device=run['config']['device'],
                project_root=self.project_root
            )
        except ValidationError as e:
            logger.error(f"Validation failed for run {run_id}: {e}")
            self.run_registry.update_run(run_id, {
                'status': 'failed',
                'error': str(e)
            })
            bus.publish(TrainingFailed(run_id=run_id, error=str(e), duration_ms=None))
            raise ValueError(str(e))

        # Get adapter
        adapter = self._get_adapter(run['task'])

        # Prepare paths
        run_path = self.project_root / run['artifacts_path']

        # Build training command
        command = adapter.build_command(
            dataset_path=dataset_path,
            output_path=run_path,
            config=run['config']
        )

        # Spawn training process
        from ...core.processes import spawn_training

        logs_dir = run_path / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        start_time = time.time()

        try:
            logger.info(f"Starting training run {run_id}")
            pid = spawn_training(
                command=command,
                cwd=run_path,
                stdout_path=logs_dir / "stdout.log",
                stderr_path=logs_dir / "stderr.log"
            )

            # Update run status
            self.run_registry.update_run(run_id, {
                'status': 'running',
                'pid': pid,
                'started': datetime.utcnow().isoformat() + 'Z'
            })

            logger.info(f"Training started: run={run_id}, pid={pid}")

            # Emit event
            bus.publish(TrainingStarted(
                run_id=run_id,
                pid=pid,
                dataset_name=run['dataset_name'],
                model=run['config']['model']
            ))

        except Exception as e:
            logger.error(f"Failed to start training run {run_id}: {e}")

            # Mark as failed
            duration_ms = int((time.time() - start_time) * 1000)
            self.run_registry.update_run(run_id, {
                'status': 'failed',
                'error': str(e),
                'duration_ms': duration_ms
            })

            bus.publish(TrainingFailed(run_id=run_id, error=str(e), duration_ms=duration_ms))
            raise RuntimeError(f"Failed to start training: {e}")

    def stop_run(self, run_id: str, timeout: float = 10.0) -> None:
        """
        Stop a running training run.

        Args:
            run_id: Run identifier
            timeout: Seconds to wait for graceful shutdown

        Raises:
            ValueError: If run doesn't exist or is not running
        """
        from ...events.training import TrainingCancelled
        from ...events.events import bus

        run = self.run_registry.get_run(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")

        if run['status'] != 'running':
            raise ValueError(f"Run {run_id} is not running (status: {run['status']})")

        pid = run.get('pid')
        if not pid:
            raise ValueError(f"No PID found for run {run_id}")

        # Terminate process
        from ...core.processes import terminate_process, is_process_alive

        logger.info(f"Stopping training run {run_id} (pid={pid})")

        try:
            terminate_process(pid, timeout=timeout)

            # Update status
            self.run_registry.update_run(run_id, {
                'status': 'cancelled',
                'pid': None
            })

            logger.info(f"Training cancelled: run={run_id}")

            # Emit event
            bus.publish(TrainingCancelled(run_id=run_id, pid=pid))

        except ProcessLookupError:
            # Process already dead
            logger.warning(f"Process {pid} already dead for run {run_id}")
            self.run_registry.update_run(run_id, {
                'status': 'cancelled',
                'pid': None
            })

            bus.publish(TrainingCancelled(run_id=run_id, pid=None))

    def get_status(self, run_id: str) -> Dict[str, Any]:
        """
        Get current status of training run.

        Args:
            run_id: Run identifier

        Returns:
            Run status dictionary

        Raises:
            ValueError: If run doesn't exist
        """
        run = self.run_registry.get_run(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")

        # Check if process is still alive
        if run['status'] == 'running' and run.get('pid'):
            from ...core.processes import is_process_alive
            if not is_process_alive(run['pid']):
                logger.info(f"Process dead for run {run_id}, finalizing")
                # Process died, check for results
                self._finalize_run(run_id)
                run = self.run_registry.get_run(run_id)

        return run

    def list_runs(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List training runs.

        Args:
            status: Filter by status (pending, running, completed, failed, cancelled)

        Returns:
            List of run dictionaries
        """
        runs = self.run_registry.list_runs()

        if status:
            runs = [r for r in runs if r['status'] == status]

        return runs

    def _generate_run_id(self) -> str:
        """Generate unique run ID with timestamp."""
        return datetime.utcnow().strftime('run-%Y%m%d-%H%M%S')

    def _resolve_device(self, device: str) -> str:
        """Resolve device string (auto -> cuda:0 or cpu)."""
        if device == "auto":
            try:
                import torch
                return "cuda:0" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return device

    def _get_adapter(self, task: str):
        """Get training adapter for task type."""
        from .adapter_yolo import YOLOAdapter
        return YOLOAdapter()

    def _finalize_run(self, run_id: str) -> None:
        """Finalize completed/failed run by parsing results."""
        from ...events.training import TrainingCompleted, TrainingFailed
        from ...events.events import bus

        run = self.run_registry.get_run(run_id)
        if not run:
            return

        run_path = self.project_root / run['artifacts_path']

        # Parse results
        adapter = self._get_adapter(run['task'])
        metrics = adapter.parse_results(run_path)

        # Calculate duration if started time exists
        duration_ms = None
        if 'started' in run:
            try:
                started = datetime.fromisoformat(run['started'].replace('Z', '+00:00'))
                now = datetime.utcnow().replace(tzinfo=started.tzinfo)
                duration_ms = int((now - started).total_seconds() * 1000)
            except:
                pass

        # Determine status
        if metrics:
            status = 'completed'
            logger.info(f"Training completed: run={run_id}, metrics={metrics}")

            # Update run
            updates = {
                'status': status,
                'metrics': metrics,
                'pid': None
            }
            if duration_ms:
                updates['duration_ms'] = duration_ms

            self.run_registry.update_run(run_id, updates)

            # Get best weights path
            best_weights = adapter.get_best_weights(run_path)
            best_weights_str = str(best_weights.relative_to(self.project_root)) if best_weights else None

            # Emit event
            bus.publish(TrainingCompleted(
                run_id=run_id,
                duration_ms=duration_ms or 0,
                metrics=metrics,
                best_weights_path=best_weights_str
            ))
        else:
            status = 'failed'
            error = "No results found - training may have crashed"
            logger.warning(f"Training failed: run={run_id}, error={error}")

            # Update run
            updates = {
                'status': status,
                'error': error,
                'pid': None
            }
            if duration_ms:
                updates['duration_ms'] = duration_ms

            self.run_registry.update_run(run_id, updates)

            # Emit event
            bus.publish(TrainingFailed(
                run_id=run_id,
                error=error,
                duration_ms=duration_ms
            ))

    def _recover_orphaned_processes(self) -> None:
        """
        Recover orphaned training processes on service init.

        Checks all runs marked as 'running' and verifies their PIDs.
        If process is dead, finalizes the run.
        """
        from ...core.processes import is_process_alive
        from ...events.training import OrphanedProcessRecovered
        from ...events.events import bus

        running_runs = self.list_runs(status='running')

        for run in running_runs:
            pid = run.get('pid')
            if not pid:
                logger.warning(f"Run {run['id']} marked running but has no PID")
                self._finalize_run(run['id'])
                continue

            if not is_process_alive(pid):
                logger.warning(f"Orphaned process detected: run={run['id']}, pid={pid}")

                # Emit event
                bus.publish(OrphanedProcessRecovered(
                    run_id=run['id'],
                    pid=pid
                ))

                # Finalize the run
                self._finalize_run(run['id'])