"""
ModelCub Project SDK.

Programmatic interface for project management.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from ..core.config import Config, load_config, save_config, create_default_config
from ..core.registries import DatasetRegistry, RunRegistry
from ..services.project_service import (
    init_project as service_init_project,
    delete_project as service_delete_project,
    InitProjectRequest,
    DeleteProjectRequest
)


class Project:
    """
    ModelCub Project - SDK interface.

    Usage:
        # Create new project
        project = Project.init("my-project")

        # Load existing project
        project = Project.load("my-project")

        # Access properties
        print(project.name)
        print(project.path)
        print(project.created)

        # Access config
        device = project.config.defaults.device
        project.config.defaults.batch_size = 32
        project.save_config()

        # Access registries
        datasets = project.datasets.list_datasets()
        runs = project.runs.list_runs()

        # Delete project
        project.delete(confirm=True)
    """

    def __init__(self, path: Path):
        """
        Initialize Project object from existing project directory.

        Use Project.load() or Project.init() instead of calling directly.
        """
        self.path = path.resolve()
        self._config: Optional[Config] = None
        self._dataset_registry: Optional[DatasetRegistry] = None
        self._run_registry: Optional[RunRegistry] = None

        # Verify it's a valid project
        if not self._is_valid_project():
            raise ValueError(f"Not a valid ModelCub project: {path}")

    def _is_valid_project(self) -> bool:
        """Check if path is a valid ModelCub project."""
        return (self.path / ".modelcub").exists() or (self.path / "modelcub.yaml").exists()

    # ========== Static Methods - Create/Load ==========

    @staticmethod
    def init(name: str, force: bool = False, path: Optional[str] = None) -> Project:
        """
        Create a new ModelCub project.

        Args:
            name: Project name (also used as directory name if path not specified)
            force: Overwrite existing project
            path: Custom directory path (default: ./<name>/)

        Returns:
            Project instance

        Example:
            >>> project = Project.init("my-project")
            >>> print(project.name)
            my-project
        """
        if path is None:
            path = name

        req = InitProjectRequest(path=path, name=name, force=force)
        code, msg = service_init_project(req)

        if code != 0:
            raise RuntimeError(f"Failed to initialize project: {msg}")

        project_path = Path(path).resolve()
        return Project(project_path)

    @staticmethod
    def load(path: str = ".") -> Project:
        """
        Load an existing ModelCub project.

        Args:
            path: Path to project directory (default: current directory)

        Returns:
            Project instance

        Example:
            >>> project = Project.load("my-project")
            >>> print(project.name)
            my-project
        """
        project_path = Path(path).resolve()
        return Project(project_path)

    @staticmethod
    def exists(path: str) -> bool:
        """
        Check if a ModelCub project exists at the given path.

        Args:
            path: Path to check

        Returns:
            True if valid project exists

        Example:
            >>> Project.exists("my-project")
            True
        """
        p = Path(path).resolve()
        return (p / ".modelcub").exists() or (p / "modelcub.yaml").exists()

    # ========== Properties ==========

    @property
    def name(self) -> str:
        """Project name from config."""
        return self.config.project.name

    @property
    def created(self) -> str:
        """Project creation timestamp."""
        return self.config.project.created

    @property
    def version(self) -> str:
        """Project version."""
        return self.config.project.version

    # ========== Config Access ==========

    @property
    def config(self) -> Config:
        """
        Access project configuration.

        Returns:
            Config object with project, defaults, and paths

        Example:
            >>> project.config.defaults.device
            'cuda'
            >>> project.config.defaults.batch_size = 32
        """
        if self._config is None:
            self._config = load_config(self.path)
            if self._config is None:
                raise RuntimeError(f"Could not load config from {self.path}")
        return self._config

    def reload_config(self) -> None:
        """Reload config from disk."""
        self._config = None

    def save_config(self) -> None:
        """
        Save config to disk.

        Example:
            >>> project.config.defaults.batch_size = 32
            >>> project.save_config()
        """
        if self._config is None:
            raise RuntimeError("No config to save")
        save_config(self.path, self._config)

    def get_config(self, key: str, default=None):
        """
        Get config value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., "defaults.device")
            default: Default value if key not found

        Returns:
            Config value

        Example:
            >>> project.get_config("defaults.device")
            'cuda'
        """
        parts = key.split(".")
        obj = self.config

        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return default

        return obj

    def set_config(self, key: str, value) -> None:
        """
        Set config value by dot-notation key.

        Args:
            key: Dot-notation key (e.g., "defaults.device")
            value: Value to set

        Example:
            >>> project.set_config("defaults.device", "cpu")
            >>> project.save_config()
        """
        parts = key.split(".")
        obj = self.config

        # Navigate to parent
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise ValueError(f"Invalid config path: {key}")

        # Set final attribute
        setattr(obj, parts[-1], value)

    # ========== Registry Access ==========

    @property
    def datasets(self) -> DatasetRegistry:
        """
        Access dataset registry.

        Returns:
            DatasetRegistry instance

        Example:
            >>> datasets = project.datasets.list_datasets()
            >>> for ds in datasets:
            ...     print(ds['name'])
        """
        if self._dataset_registry is None:
            self._dataset_registry = DatasetRegistry(self.path)
        return self._dataset_registry

    @property
    def runs(self) -> RunRegistry:
        """
        Access run registry.

        Returns:
            RunRegistry instance

        Example:
            >>> runs = project.runs.list_runs()
        """
        if self._run_registry is None:
            self._run_registry = RunRegistry(self.path)
        return self._run_registry

    # ========== Directory Paths ==========

    @property
    def modelcub_dir(self) -> Path:
        """Path to .modelcub/ directory."""
        return self.path / ".modelcub"

    @property
    def data_dir(self) -> Path:
        """Path to data/ directory."""
        return self.path / self.config.paths.data

    @property
    def datasets_dir(self) -> Path:
        """Path to data/datasets/ directory."""
        return self.data_dir / "datasets"

    @property
    def runs_dir(self) -> Path:
        """Path to runs/ directory."""
        return self.path / self.config.paths.runs

    @property
    def reports_dir(self) -> Path:
        """Path to reports/ directory."""
        return self.path / self.config.paths.reports

    @property
    def cache_dir(self) -> Path:
        """Path to .modelcub/cache/ directory."""
        return self.modelcub_dir / "cache"

    @property
    def backups_dir(self) -> Path:
        """Path to .modelcub/backups/ directory."""
        return self.modelcub_dir / "backups"

    @property
    def history_dir(self) -> Path:
        """Path to .modelcub/history/ directory."""
        return self.modelcub_dir / "history"

    # ========== Project Management ==========

    def delete(self, confirm: bool = False) -> None:
        """
        Delete this project.

        Args:
            confirm: Must be True to actually delete

        Example:
            >>> project.delete(confirm=True)
        """
        if not confirm:
            raise RuntimeError("Must set confirm=True to delete project")

        req = DeleteProjectRequest(target=str(self.path), yes=True)
        code, msg = service_delete_project(req)

        if code != 0:
            raise RuntimeError(f"Failed to delete project: {msg}")

    # ========== String Representation ==========

    def __repr__(self) -> str:
        return f"Project(name='{self.name}', path='{self.path}')"

    def __str__(self) -> str:
        return f"ModelCub Project: {self.name} ({self.path})"

    # ========== Context Manager ==========

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - save config if modified."""
        if self._config is not None:
            self.save_config()