"""
ModelCub Dataset SDK.

Elegant, pythonic interface for dataset operations.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

from ..services.image_service import import_images, ImportImagesRequest
from ..core.paths import project_root, datasets_dir
from ..core.images import scan_directory, format_size


@dataclass
class DatasetInfo:
    """Dataset information container."""
    name: str
    path: Path
    status: str
    classes: List[str]
    total_images: int
    train_images: int = 0
    valid_images: int = 0
    unlabeled_images: int = 0
    size_bytes: int = 0
    source: Optional[str] = None

    @property
    def size(self) -> str:
        """Human-readable size."""
        return format_size(self.size_bytes)

    def __repr__(self) -> str:
        return (
            f"Dataset(name='{self.name}', "
            f"images={self.total_images}, "
            f"status='{self.status}')"
        )


class Dataset:
    """
    ModelCub Dataset - SDK interface.

    Usage:
        # Import from images
        dataset = Dataset.from_images("./photos", name="my-photos")

        # Load existing dataset
        dataset = Dataset.load("my-photos")

        # Access properties
        print(dataset.name)
        print(dataset.images)
        print(dataset.classes)

        # Get detailed info
        info = dataset.info()
        print(info.total_images)
        print(info.size)

        # Manage classes
        dataset.add_class('cat')
        dataset.add_class('dog')
        classes = dataset.list_classes()
    """

    def __init__(self, name: str):
        """
        Initialize Dataset from existing dataset.

        Use Dataset.load() or Dataset.from_*() instead of calling directly.
        """
        self.name = name
        self._path = datasets_dir() / name

        if not self._path.exists():
            raise ValueError(f"Dataset not found: {name}")

        self._manifest: Optional[dict] = None
        self._load_manifest()

    def _load_manifest(self) -> None:
        """Load dataset manifest."""
        manifest_path = self._path / "manifest.json"
        if manifest_path.exists():
            self._manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        else:
            self._manifest = {}

    # ========== Static Methods - Import/Load ==========

    @staticmethod
    def from_images(
        source: str | Path,
        name: Optional[str] = None,
        recursive: bool = False,
        copy: bool = True,
        validate: bool = True
    ) -> Dataset:
        """
        Import images from a directory.

        Args:
            source: Path to directory containing images
            name: Optional dataset name (auto-generated if not provided)
            recursive: Scan subdirectories recursively
            copy: Copy files (True) or create symlinks (False)
            validate: Validate images during import

        Returns:
            Dataset instance

        Raises:
            ValueError: If import fails

        Example:
            >>> dataset = Dataset.from_images("./photos", name="my-photos")
            >>> print(dataset.images)
            42
        """
        root = project_root()

        req = ImportImagesRequest(
            project_path=root,
            source=Path(source),
            dataset_name=name,
            copy=copy,
            validate=validate,
            recursive=recursive,
            force=False
        )

        result = import_images(req)

        if not result.success:
            raise ValueError(f"Failed to import dataset: {result.message}")

        return Dataset(result.dataset_name)

    @staticmethod
    def load(name: str) -> Dataset:
        """
        Load an existing dataset.

        Args:
            name: Dataset name

        Returns:
            Dataset instance

        Raises:
            ValueError: If dataset not found

        Example:
            >>> dataset = Dataset.load("my-photos")
        """
        return Dataset(name)

    @staticmethod
    def list() -> List[Dataset]:
        """
        List all datasets in the current project.

        Returns:
            List of Dataset instances

        Example:
            >>> datasets = Dataset.list()
            >>> for ds in datasets:
            ...     print(ds.name, ds.images)
        """
        from ..core.registries import DatasetRegistry

        root = project_root()
        registry = DatasetRegistry(root)
        dataset_list = registry.list_datasets()

        datasets = []
        for ds_dict in dataset_list:
            try:
                dataset = Dataset(ds_dict["name"])
                datasets.append(dataset)
            except Exception:
                continue

        return datasets

    @staticmethod
    def exists(name: str) -> bool:
        """
        Check if a dataset exists.

        Args:
            name: Dataset name

        Returns:
            True if dataset exists, False otherwise

        Example:
            >>> if Dataset.exists("my-photos"):
            ...     dataset = Dataset.load("my-photos")
        """
        from ..core.registries import DatasetRegistry

        root = project_root()
        registry = DatasetRegistry(root)
        return registry.exists(name)

    # ========== Properties ==========

    @property
    def path(self) -> Path:
        """Path to dataset directory."""
        return self._path

    @property
    def id(self) -> str:
        """Dataset unique ID."""
        return self._manifest.get("id", "")

    @property
    def status(self) -> str:
        """Dataset status (e.g., 'unlabeled', 'ready')."""
        return self._manifest.get("status", "unknown")

    @property
    def classes(self) -> List[str]:
        """List of class names."""
        return self._manifest.get("classes", [])

    @property
    def images(self) -> int:
        """Total number of images."""
        images_dict = self._manifest.get("images", {})
        return images_dict.get("total", 0)

    @property
    def size_bytes(self) -> int:
        """Dataset size in bytes."""
        return self._manifest.get("size_bytes", 0)

    @property
    def size(self) -> str:
        """Human-readable dataset size."""
        return format_size(self.size_bytes)

    # ========== Methods ==========

    def info(self) -> DatasetInfo:
        """
        Get detailed dataset information.

        Returns:
            DatasetInfo object with all metadata

        Example:
            >>> info = dataset.info()
            >>> print(f"{info.name}: {info.total_images} images, {info.size}")
        """
        images_dict = self._manifest.get("images", {})

        return DatasetInfo(
            name=self.name,
            path=self._path,
            status=self.status,
            classes=self.classes,
            total_images=images_dict.get("total", 0),
            train_images=images_dict.get("train", 0),
            valid_images=images_dict.get("val", 0),
            unlabeled_images=images_dict.get("unlabeled", 0),
            size_bytes=self.size_bytes,
            source=self._manifest.get("source")
        )

    def delete(self, confirm: bool = False) -> None:
        """
        Delete this dataset.

        Args:
            confirm: Must be True to actually delete

        Raises:
            ValueError: If confirm is not True

        Example:
            >>> dataset.delete(confirm=True)
        """
        if not confirm:
            raise ValueError("Must pass confirm=True to delete dataset")

        from ..core.registries import DatasetRegistry
        import shutil

        root = project_root()
        registry = DatasetRegistry(root)

        # Remove from registry
        registry.remove_dataset(self.name)
        registry.save()

        # Delete directory
        if self._path.exists():
            shutil.rmtree(self._path)

    # ========== Class Management ==========

    def list_classes(self) -> List[str]:
        """
        List all classes in this dataset.

        Returns:
            List of class names

        Example:
            >>> classes = dataset.list_classes()
            >>> print(classes)
            ['cat', 'dog', 'bird']
        """
        from ..core.registries import DatasetRegistry

        root = project_root()
        registry = DatasetRegistry(root)
        return registry.list_classes(self.name)

    def add_class(self, class_name: str, class_id: Optional[int] = None) -> int:
        """
        Add a new class to this dataset.

        Args:
            class_name: Name of the class to add
            class_id: Optional specific ID for the class (auto-assigned if None)

        Returns:
            Assigned class ID

        Raises:
            ValueError: If class already exists or class_id is invalid

        Example:
            >>> dataset.add_class('cat')
            0
            >>> dataset.add_class('dog')
            1
            >>> dataset.add_class('fish', class_id=5)
            5
        """
        from ..core.registries import DatasetRegistry
        from ..core.exceptions import ClassExistsError

        root = project_root()
        registry = DatasetRegistry(root)

        try:
            assigned_id = registry.add_class(self.name, class_name, class_id)
            self._load_manifest()  # Reload manifest to get updated classes
            return assigned_id
        except ClassExistsError as e:
            raise ValueError(str(e))

    def remove_class(self, class_name: str) -> None:
        """
        Remove a class from this dataset.

        Note: This does not delete existing labels with this class.

        Args:
            class_name: Name of the class to remove

        Raises:
            ValueError: If class not found

        Example:
            >>> dataset.remove_class('cat')
        """
        from ..core.registries import DatasetRegistry
        from ..core.exceptions import ClassNotFoundError

        root = project_root()
        registry = DatasetRegistry(root)

        try:
            registry.remove_class(self.name, class_name)
            self._load_manifest()  # Reload manifest
        except ClassNotFoundError as e:
            raise ValueError(str(e))

    def rename_class(self, old_name: str, new_name: str) -> None:
        """
        Rename a class in this dataset.

        Args:
            old_name: Current class name
            new_name: New class name

        Raises:
            ValueError: If old class not found or new name already exists

        Example:
            >>> dataset.rename_class('cat', 'feline')
        """
        from ..core.registries import DatasetRegistry
        from ..core.exceptions import ClassNotFoundError, ClassExistsError

        root = project_root()
        registry = DatasetRegistry(root)

        try:
            registry.rename_class(self.name, old_name, new_name)
            self._load_manifest()  # Reload manifest
        except (ClassNotFoundError, ClassExistsError) as e:
            raise ValueError(str(e))

    def __repr__(self) -> str:
        return f"Dataset(name='{self.name}', images={self.images}, status='{self.status}')"