"""
ModelCub SDK - Training Run Management.

Provides high-level Python API for training operations.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import time


@dataclass
class RunMetrics:
    """Training run metrics."""
    map50: Optional[float] = None
    map50_95: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    best_epoch: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RunMetrics:
        """Create metrics from dictionary."""
        return cls(
            map50=data.get('map50'),
            map50_95=data.get('map50_95'),
            precision=data.get('precision'),
            recall=data.get('recall'),
            best_epoch=data.get('best_epoch')
        )


class TrainingRun:
    """
    High-level interface for a single training run.

    Example:
        >>> run = TrainingRun("run-20251027-143022", project_path="/path/to/project")
        >>> run.start()
        >>> while run.status == "running":
        ...     print(f"Status: {run.status}")
        ...     time.sleep(5)
        ...     run.reload()
        >>> print(f"mAP50: {run.metrics.map50}")
    """

    def __init__(self, run_id: str, project_path: str | Path):
        """
        Initialize TrainingRun.

        Args:
            run_id: Run identifier
            project_path: Project directory path
        """
        self.run_id = run_id
        self._project_path = Path(project_path).resolve()
        self._data = None
        self._load_data()

    def _load_data(self) -> None:
        """Load run data from registry."""
        from ..services.training.training_service import TrainingService

        service = TrainingService(self._project_path)
        self._data = service.get_status(self.run_id)

    # ========== Properties ==========

    @property
    def id(self) -> str:
        """Run ID."""
        return self.run_id

    @property
    def status(self) -> str:
        """
        Current run status.

        Returns:
            One of: 'pending', 'running', 'completed', 'failed', 'cancelled'
        """
        return self._data['status']

    @property
    def dataset_name(self) -> str:
        """Name of the dataset used for training."""
        return self._data['dataset_name']

    @property
    def model(self) -> str:
        """Model architecture (e.g., yolov8n)."""
        return self._data['config']['model']

    @property
    def task(self) -> str:
        """Task type (detect, segment, classify)."""
        return self._data['task']

    @property
    def created(self) -> str:
        """ISO timestamp of when run was created."""
        return self._data['created']

    @property
    def config(self) -> Dict[str, Any]:
        """Training configuration dictionary."""
        return self._data['config']

    @property
    def metrics(self) -> RunMetrics:
        """Training metrics (mAP, precision, recall, etc.)."""
        return RunMetrics.from_dict(self._data.get('metrics', {}))

    @property
    def artifacts_path(self) -> Path:
        """Path to run artifacts directory."""
        return self._project_path / self._data['artifacts_path']

    @property
    def pid(self) -> Optional[int]:
        """Process ID if running, None otherwise."""
        return self._data.get('pid')

    @property
    def error(self) -> Optional[str]:
        """Error message if failed, None otherwise."""
        return self._data.get('error')

    @property
    def duration_ms(self) -> Optional[int]:
        """Training duration in milliseconds."""
        return self._data.get('duration_ms')

    # ========== Core Methods ==========

    def start(self) -> None:
        """
        Start training run.

        Raises:
            ValueError: If run is not in pending status

        Example:
            >>> run.start()
        """
        from ..services.training.training_service import TrainingService

        service = TrainingService(self._project_path)
        service.start_run(self.run_id)
        self.reload()

    def stop(self, timeout: float = 10.0) -> None:
        """
        Stop running training.

        Args:
            timeout: Seconds to wait for graceful shutdown

        Raises:
            ValueError: If run is not running

        Example:
            >>> run.stop()
            >>> run.stop(timeout=30.0)
        """
        from ..services.training.training_service import TrainingService

        service = TrainingService(self._project_path)
        service.stop_run(self.run_id, timeout=timeout)
        self.reload()

    def reload(self) -> None:
        """
        Reload run data from registry.

        Example:
            >>> run.reload()
            >>> print(run.status)  # Updated status
        """
        self._load_data()

    def wait(self, poll_interval: float = 5.0, timeout: Optional[float] = None) -> str:
        """
        Wait for training to complete.

        Args:
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait (None = no timeout)

        Returns:
            Final status ('completed', 'failed', or 'cancelled')

        Example:
            >>> final_status = run.wait()
            >>> print(f"Training finished with status: {final_status}")
        """
        start_time = time.time()

        while self.status in ['pending', 'running']:
            time.sleep(poll_interval)
            self.reload()

            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Training did not complete within {timeout}s")

        return self.status

    def get_logs(
        self,
        stream: str = 'stdout',
        lines: Optional[int] = None,
        follow: bool = False
    ) -> List[str]:
        """
        Get training logs.

        Args:
            stream: 'stdout' or 'stderr'
            lines: Number of lines to return (None = all)
            follow: If True, yield new lines as they appear

        Returns:
            List of log lines

        Example:
            >>> logs = run.get_logs(lines=50)
            >>> for line in logs:
            ...     print(line)
        """
        log_file = self.artifacts_path / 'logs' / f'{stream}.log'

        if not log_file.exists():
            return []

        with open(log_file, 'r') as f:
            if lines:
                all_lines = f.readlines()
                return all_lines[-lines:]
            else:
                return f.readlines()

    def delete(self, keep_artifacts: bool = False) -> None:
        """
        Delete this training run.

        Args:
            keep_artifacts: If True, only remove from registry but keep files

        Raises:
            ValueError: If run is currently running

        Example:
            >>> run.delete()
            >>> run.delete(keep_artifacts=True)
        """
        from ..services.training.training_service import TrainingService
        import shutil

        if self.status == 'running':
            raise ValueError("Cannot delete running run. Stop it first.")

        # Delete artifacts if requested
        if not keep_artifacts and self.artifacts_path.exists():
            shutil.rmtree(self.artifacts_path)

        # Remove from registry
        service = TrainingService(self._project_path)
        service.run_registry.remove_run(self.run_id)

    # ========== Utility Methods ==========

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert run to dictionary.

        Returns:
            Dictionary with all run information

        Example:
            >>> data = run.to_dict()
            >>> print(data['status'])
        """
        return self._data.copy()

    def __repr__(self) -> str:
        """String representation."""
        return f"TrainingRun(id='{self.run_id}', status='{self.status}', model='{self.model}')"


class TrainingManager:
    """
    High-level interface for managing training runs.

    Example:
        >>> from modelcub import Project
        >>> project = Project.load()
        >>> training = project.training
        >>> run = training.create("my-dataset", model="yolov8n", epochs=100)
        >>> run.start()
    """

    def __init__(self, project_path: str | Path):
        """
        Initialize TrainingManager.

        Args:
            project_path: Project directory path
        """
        self._project_path = Path(project_path).resolve()

    def create(
        self,
        dataset_name: str,
        model: str = 'yolov8n',
        epochs: int = 100,
        task: str = 'detect',
        imgsz: int = 640,
        batch: int = 16,
        device: str = 'auto',
        patience: int = 50,
        save_period: int = 10,
        workers: int = 8,
        seed: Optional[int] = None,
        **kwargs
    ) -> TrainingRun:
        """
        Create a new training run.

        Args:
            dataset_name: Name of dataset to train on
            model: Model architecture (yolov8n, yolov8s, yolov8m, yolov8l, yolov8x)
            epochs: Number of training epochs
            task: Task type ('detect', 'segment', 'classify')
            imgsz: Input image size
            batch: Batch size
            device: Device ('auto', 'cpu', 'cuda', 'cuda:0', etc.)
            patience: Early stopping patience
            save_period: Save checkpoint every N epochs
            workers: Number of data loading workers
            seed: Random seed for reproducibility
            **kwargs: Additional training parameters

        Returns:
            TrainingRun instance

        Example:
            >>> run = training.create(
            ...     "my-dataset",
            ...     model="yolov8s",
            ...     epochs=50,
            ...     batch=32,
            ...     device="cuda:0"
            ... )
        """
        from ..services.training.training_service import TrainingService

        service = TrainingService(self._project_path)

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
            seed=seed,
            **kwargs
        )

        return TrainingRun(run_id, self._project_path)

    def get(self, run_id: str) -> TrainingRun:
        """
        Get a training run by ID.

        Args:
            run_id: Run identifier

        Returns:
            TrainingRun instance

        Raises:
            ValueError: If run not found

        Example:
            >>> run = training.get("run-20251027-143022")
        """
        return TrainingRun(run_id, self._project_path)

    def list(
        self,
        status: Optional[str] = None
    ) -> List[TrainingRun]:
        """
        List all training runs.

        Args:
            status: Filter by status ('pending', 'running', 'completed', 'failed', 'cancelled')

        Returns:
            List of TrainingRun instances

        Example:
            >>> all_runs = training.list()
            >>> running = training.list(status='running')
            >>> completed = training.list(status='completed')
        """
        from ..services.training.training_service import TrainingService

        service = TrainingService(self._project_path)
        runs_data = service.list_runs(status=status)

        return [TrainingRun(r['id'], self._project_path) for r in runs_data]

    def purge(self, keep_artifacts: bool = False) -> int:
        """
        Delete all training runs.

        Args:
            keep_artifacts: If True, only remove from registry but keep files

        Returns:
            Number of runs deleted

        Raises:
            ValueError: If any runs are currently running

        Example:
            >>> deleted_count = training.purge()
            >>> print(f"Deleted {deleted_count} runs")
        """
        runs = self.list()

        # Check for running runs
        running = [r for r in runs if r.status == 'running']
        if running:
            raise ValueError(
                f"Cannot purge: {len(running)} run(s) still running. "
                "Stop them first."
            )

        # Delete all runs
        deleted = 0
        for run in runs:
            run.delete(keep_artifacts=keep_artifacts)
            deleted += 1

        return deleted

    def __repr__(self) -> str:
        """String representation."""
        return f"TrainingManager(project='{self._project_path.name}')"