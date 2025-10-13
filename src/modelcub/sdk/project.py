"""
ModelCub Project SDK.

High-level interface for project operations.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, List

from ..services.project_service import (
    init_project, delete_project,
    InitProjectRequest, DeleteProjectRequest
)
from ..services.image_service import import_images, ImportImagesRequest
from ..core.config import load_config, save_config
from ..core.registries import DatasetRegistry
from .dataset import Dataset


class Project:
    """
    ModelCub Project - SDK interface.

    Usage:
        # Create new project
        project = Project.init("my-project")

        # Load existing project
        project = Project.load("path/to/project")

        # Import dataset
        dataset = project.import_dataset(
            source="./photos",
            name="animals",
            classes=["cat", "dog", "bird"]
        )

        # List datasets
        datasets = project.list_datasets()

        # Access config
        project.config.defaults.batch_size = 32
        project.save_config()
    """

    def __init__(self, path: Path):
        """
        Initialize Project.

        Use Project.init() or Project.load() instead of calling directly.
        """
        self.path = Path(path).resolve()

        if not (self.path / ".modelcub").exists():
            raise ValueError(f"Not a ModelCub project: {path}")

        self._config = None
        self._load_config()

    def _load_config(self) -> None:
        """Load project configuration."""
        self._config = load_config(self.path)

    # ========== Static Methods ==========

    @staticmethod
    def init(
        name: str,
        path: str | Path = ".",
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
            >>> project = Project.init("my-project")
            >>> print(project.name)
            my-project
        """
        req = InitProjectRequest(
            path=str(path),
            name=name,
            force=force
        )

        code, msg = init_project(req)

        if code != 0:
            raise ValueError(msg)

        project_path = Path(path).resolve()
        return Project(project_path)

    @staticmethod
    def load(path: str | Path = ".") -> Project:
        """
        Load an existing ModelCub project.

        Args:
            path: Project directory (default: current directory)

        Returns:
            Project instance

        Example:
            >>> project = Project.load(".")
        """
        return Project(Path(path))

    @staticmethod
    def exists(path: str | Path = ".") -> bool:
        """
        Check if a ModelCub project exists.

        Args:
            path: Project directory

        Returns:
            True if project exists

        Example:
            >>> if Project.exists("."):
            ...     project = Project.load()
        """
        return (Path(path) / ".modelcub").exists()

    # ========== Properties ==========

    @property
    def name(self) -> str:
        """Project name."""
        return self._config.project.name if self._config else ""

    @property
    def created(self) -> str:
        """Project creation timestamp."""
        return self._config.project.created if self._config else ""

    @property
    def version(self) -> str:
        """Project version."""
        return self._config.project.version if self._config else ""

    @property
    def config(self):
        """Project configuration object."""
        return self._config

    @property
    def datasets(self) -> DatasetRegistry:
        """Dataset registry."""
        return DatasetRegistry(self.path)

    # ========== Dataset Operations ==========

    def import_dataset(
        self,
        source: str | Path,
        name: Optional[str] = None,
        classes: Optional[List[str]] = None,
        recursive: bool = False,
        copy: bool = True,
        validate: bool = True,
        force: bool = False
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

        Returns:
            Dataset instance

        Example:
            >>> dataset = project.import_dataset(
            ...     source="./photos",
            ...     name="animals",
            ...     classes=["cat", "dog", "bird"]
            ... )
        """
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

        return Dataset(result.dataset_name)

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
                dataset = Dataset(ds_dict["name"])
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
            >>> dataset = project.get_dataset("animals")
        """
        if not self.datasets.exists(name):
            raise ValueError(f"Dataset not found: {name}")
        return Dataset(name)

    # ========== Configuration ==========

    def save_config(self) -> None:
        """
        Save configuration to disk.

        Example:
            >>> project.config.defaults.batch_size = 32
            >>> project.save_config()
        """
        if self._config:
            save_config(self.path, self._config)

    # ========== Project Management ==========

    def delete(self, confirm: bool = False) -> None:
        """
        Delete this project.

        Args:
            confirm: Must be True to actually delete

        Raises:
            ValueError: If confirm is not True

        Example:
            >>> project.delete(confirm=True)
        """
        if not confirm:
            raise ValueError("Must pass confirm=True to delete project")

        req = DeleteProjectRequest(
            target=str(self.path),
            yes=True
        )

        code, msg = delete_project(req)

        if code != 0:
            raise ValueError(msg)

    def __repr__(self) -> str:
        return f"ModelCub Project: {self.name} ({self.path})"

    def __str__(self) -> str:
        return self.__repr__()