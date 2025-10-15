"""
ModelCub SDK - Project Management.

Provides high-level Python API for project operations.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Any
import shutil

from ..services.project_service import (
    init_project,
    delete_project,
    InitProjectRequest,
    DeleteProjectRequest
)
from ..core.config import Config, load_config, save_config
from ..core.registries import DatasetRegistry, RunRegistry
from ..core.paths import project_root
from .dataset import Dataset


class Project:
    """
    High-level interface for ModelCub projects.

    Example:
        >>> project = Project.init("my-project")
        >>> dataset = project.import_dataset(source="./images", classes=["cat", "dog"])
        >>> datasets = project.list_datasets()
    """

    def __init__(self, path: str | Path):
        """Initialize Project by loading from path."""
        self.path = Path(path).resolve()

        if not self._is_valid_project(self.path):
            raise ValueError(f"Not a valid ModelCub project: {self.path}")

        self._config = load_config(self.path)

    @staticmethod
    def _is_valid_project(path: Path) -> bool:
        """Check if directory is a valid ModelCub project."""
        return (path / ".modelcub").exists() and (path / ".modelcub" / "config.yaml").exists()

    # ========== Static Methods ==========

    @classmethod
    def init(
        cls,
        name: str,
        path: Optional[str | Path] = None,
        force: bool = False
    ) -> Project:
        """
        Initialize a new ModelCub project.

        Args:
            name: Project name
            path: Project directory (default: current directory)
            force: Overwrite existing project

        Returns:
            Project instance

        Example:
            >>> project = Project.init("my-cv-project")
            >>> project = Project.init("detection", path="/workspace/proj")
        """
        target_path = Path(path) if path else Path.cwd() / name
        target_path = target_path.resolve()

        req = InitProjectRequest(
            path=str(target_path),
            name=name,
            force=force
        )

        code, msg = init_project(req)

        if code != 0:
            raise RuntimeError(f"Failed to initialize project: {msg}")

        return cls(target_path)

    @classmethod
    def load(cls, path: Optional[str | Path] = None) -> Project:
        """
        Load existing ModelCub project.

        Args:
            path: Project directory (default: search upward from current directory)

        Returns:
            Project instance

        Example:
            >>> project = Project.load()
            >>> project = Project.load("/path/to/project")
        """
        if path is None:
            path = project_root()
        else:
            path = Path(path).resolve()

        return cls(path)

    @staticmethod
    def exists(path: str | Path = ".") -> bool:
        """
        Check if a ModelCub project exists at path.

        Args:
            path: Project directory

        Returns:
            True if valid project exists

        Example:
            >>> if Project.exists("./my-project"):
            ...     project = Project.load("./my-project")
        """
        path = Path(path).resolve()
        return (path / ".modelcub").exists() and (path / ".modelcub" / "config.yaml").exists()

    # ========== Properties ==========

    @property
    def name(self) -> str:
        """Project name."""
        return self._config.project.name

    @property
    def created(self) -> str:
        """Project creation timestamp."""
        return self._config.project.created

    @property
    def version(self) -> str:
        """Project version."""
        return self._config.project.version

    @property
    def config(self) -> Config:
        """Project configuration."""
        return self._config

    @property
    def datasets(self) -> DatasetRegistry:
        """Dataset registry."""
        return DatasetRegistry(self.path)

    @property
    def runs(self) -> RunRegistry:
        """Training runs registry."""
        return RunRegistry(self.path)

    # ========== Path Properties ==========

    @property
    def modelcub_dir(self) -> Path:
        """Path to .modelcub directory."""
        return self.path / ".modelcub"

    @property
    def data_dir(self) -> Path:
        """Path to data directory."""
        return self.path / self._config.paths.data

    @property
    def datasets_dir(self) -> Path:
        """Path to datasets directory."""
        return self.data_dir / "datasets"

    @property
    def runs_dir(self) -> Path:
        """Path to runs directory."""
        return self.path / self._config.paths.runs

    @property
    def reports_dir(self) -> Path:
        """Path to reports directory."""
        return self.path / self._config.paths.reports

    @property
    def cache_dir(self) -> Path:
        """Path to cache directory."""
        return self.modelcub_dir / "cache"

    @property
    def backups_dir(self) -> Path:
        """Path to backups directory."""
        return self.modelcub_dir / "backups"

    @property
    def history_dir(self) -> Path:
        """Path to history directory."""
        return self.modelcub_dir / "history"

    # ========== Config Methods ==========

    def save_config(self) -> None:
        """Save current configuration to disk."""
        save_config(self.path, self._config)

    def reload_config(self) -> None:
        """Reload configuration from disk."""
        self._config = load_config(self.path)

    def get_config(self, path: str, default: Any = None) -> Any:
        """
        Get config value by dot-separated path.

        Args:
            path: Dot-separated config path (e.g., "defaults.batch_size")
            default: Default value if not found

        Returns:
            Config value or default

        Example:
            >>> project.get_config("defaults.device")
            'cuda'
            >>> project.get_config("foo.bar", "fallback")
            'fallback'
        """
        parts = path.split(".")
        value = self._config

        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                return default

        return value

    def set_config(self, path: str, value: Any) -> None:
        """
        Set config value by dot-separated path.

        Args:
            path: Dot-separated config path
            value: Value to set

        Raises:
            ValueError: If path is invalid

        Example:
            >>> project.set_config("defaults.batch_size", 64)
            >>> project.save_config()
        """
        parts = path.split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid config path: {path}")

        obj = self._config
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise ValueError(f"Invalid config path: {path}")

        final_attr = parts[-1]
        if not hasattr(obj, final_attr):
            raise ValueError(f"Invalid config path: {path}")

        setattr(obj, final_attr, value)

    # ========== Project Operations ==========

    def delete(self, confirm: bool = False) -> None:
        """
        Delete this project.

        Args:
            confirm: Must be True to actually delete

        Raises:
            RuntimeError: If confirm is False

        Example:
            >>> project = Project.load()
            >>> project.delete(confirm=True)
        """
        if not confirm:
            raise RuntimeError("Must set confirm=True to delete project")

        req = DeleteProjectRequest(
            target=str(self.path),
            yes=True
        )

        code, msg = delete_project(req)

        if code != 0:
            raise RuntimeError(f"Failed to delete project: {msg}")

    # ========== Dataset Operations ==========

    def import_dataset(
    self,
    source: str | Path,
    name: Optional[str] = None,
    classes: Optional[List[str]] = None,
    recursive: bool = False,
    copy: bool = True,
    validate: bool = True,
    force: bool = False,
    delete_existent: bool = False
) -> Dataset:
        """
        Import images as a dataset into this project.

        Args:
            source: Path to directory containing images
            name: Dataset name (auto-generated if not provided)
            classes: List of class names
            recursive: Scan subdirectories recursively
            copy: Copy files (True) or create symlinks (False)
            validate: Validate images during import
            force: Overwrite existing dataset
            delete_existent: Delete existing dataset before import

        Returns:
            Dataset instance

        Example:
            >>> dataset = project.import_dataset(
            ...     source="./photos",
            ...     name="animals",
            ...     classes=["cat", "dog", "bird"],
            ...     delete_existent=True
            ... )
        """
        from ..services.image_service import import_images, ImportImagesRequest

        # Delete existing dataset if requested
        if delete_existent and name:
            dataset_path = self.datasets_dir / name
            if dataset_path.exists():
                import shutil
                shutil.rmtree(dataset_path)

                # Remove from registry
                registry = DatasetRegistry(self.path)
                try:
                    registry.remove_dataset(name)
                except:
                    pass  # Ignore if not in registry

        # Parse classes from string if needed
        if isinstance(classes, str):
            classes = [c.strip() for c in classes.split(",") if c.strip()]

        req = ImportImagesRequest(
            project_path=self.path,
            source=Path(source),
            dataset_name=name,
            classes=classes,
            copy=copy,
            validate=validate,
            recursive=recursive,
            force=force
        )

        result = import_images(req)

        if not result.success:
            raise ValueError(result.message)

        return Dataset(result.dataset_name, project_path=self.path)

    def list_datasets(self) -> List[Dataset]:
        """
        List all datasets in this project.

        Returns:
            List of Dataset instances

        Example:
            >>> for dataset in project.list_datasets():
            ...     print(dataset.name, dataset.images)
        """
        registry = DatasetRegistry(self.path)
        dataset_list = registry.list_datasets()

        datasets = []
        for ds_dict in dataset_list:
            try:
                dataset = Dataset(ds_dict["name"], project_path=self.path)
                datasets.append(dataset)
            except Exception:
                continue

        return datasets

    def get_dataset(self, name: str) -> Dataset:
        """
        Get a dataset by name.

        Args:
            name: Dataset name

        Returns:
            Dataset instance

        Raises:
            ValueError: If dataset not found

        Example:
            >>> dataset = project.get_dataset("animals-v1")
        """
        registry = DatasetRegistry(self.path)
        ds_dict = registry.get_dataset(name)

        if not ds_dict:
            raise ValueError(f"Dataset not found: {name}")

        return Dataset(name, project_path=self.path)

    # ========== Context Manager ==========

    def __enter__(self) -> Project:
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager - auto-save config."""
        self.save_config()

    # ========== String Representations ==========

    def __repr__(self) -> str:
        return f"Project(name='{self.name}', path='{self.path}')"

    def __str__(self) -> str:
        return f"ModelCub Project: {self.name}"