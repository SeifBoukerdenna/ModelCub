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
            source: Directory containing images
            name: Dataset name (auto-generated if not provided)
            recursive: Scan subdirectories
            copy: Copy files (True) or create symlinks (False)
            validate: Validate images during import

        Returns:
            Dataset instance

        Example:
            >>> dataset = Dataset.from_images("./photos")
            >>> print(dataset.name)
            photos-20251012-143022

            >>> dataset = Dataset.from_images(
            ...     "./photos",
            ...     name="my-photos",
            ...     recursive=True
            ... )
        """
        req = ImportImagesRequest(
            source=source,
            name=name,
            copy=copy,
            validate=validate,
            recursive=recursive,
            force=False
        )

        code, msg = import_images(req)

        if code != 0:
            raise RuntimeError(f"Failed to import images: {msg}")

        # Extract dataset name from success message
        # Format: "Name: <name>"
        for line in msg.split("\n"):
            if line.strip().startswith("Name:"):
                imported_name = line.split(":", 1)[1].strip()
                return Dataset(imported_name)

        # Fallback: use provided name or try to infer
        if name:
            return Dataset(name)

        raise RuntimeError("Failed to determine imported dataset name")

    @staticmethod
    def from_yolo(
        source: str | Path,
        name: Optional[str] = None
    ) -> Dataset:
        """
        Import dataset from YOLO format.

        Args:
            source: Directory containing YOLO dataset
            name: Dataset name

        Returns:
            Dataset instance

        Example:
            >>> dataset = Dataset.from_yolo("./yolo_data", name="my-dataset")

        Note:
            This feature is coming soon. Use Dataset.from_images() for now.
        """
        raise NotImplementedError(
            "YOLO import coming soon. "
            "Use Dataset.from_images() to import unlabeled images."
        )

    @staticmethod
    def from_roboflow(
        export_zip: str | Path,
        name: Optional[str] = None
    ) -> Dataset:
        """
        Import dataset from Roboflow export ZIP.

        Args:
            export_zip: Path to Roboflow export ZIP file
            name: Dataset name

        Returns:
            Dataset instance

        Example:
            >>> dataset = Dataset.from_roboflow("export.zip", name="my-dataset")

        Note:
            This feature is coming soon.
        """
        raise NotImplementedError("Roboflow import coming soon")

    @staticmethod
    def load(name: str) -> Dataset:
        """
        Load an existing dataset.

        Args:
            name: Dataset name

        Returns:
            Dataset instance

        Example:
            >>> dataset = Dataset.load("my-photos")
            >>> print(dataset.images)
            309
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
            ...     print(f"{ds.name}: {ds.images} images")
        """
        data_dir = datasets_dir()
        if not data_dir.exists():
            return []

        datasets = []
        for path in sorted(data_dir.iterdir()):
            if path.is_dir():
                manifest_path = path / "manifest.json"
                if manifest_path.exists():
                    try:
                        datasets.append(Dataset(path.name))
                    except:
                        pass

        return datasets

    @staticmethod
    def exists(name: str) -> bool:
        """
        Check if a dataset exists.

        Args:
            name: Dataset name

        Returns:
            True if dataset exists

        Example:
            >>> if Dataset.exists("my-photos"):
            ...     dataset = Dataset.load("my-photos")
        """
        path = datasets_dir() / name
        return path.exists() and (path / "manifest.json").exists()

    # ========== Properties ==========

    @property
    def path(self) -> Path:
        """Dataset directory path."""
        return self._path

    @property
    def id(self) -> str:
        """Dataset ID."""
        return self._manifest.get("id", "")

    @property
    def status(self) -> str:
        """Dataset status (labeled, unlabeled, partially-labeled)."""
        return self._manifest.get("status", "unknown")

    @property
    def classes(self) -> List[str]:
        """List of class names."""
        return self._manifest.get("classes", [])

    @property
    def images(self) -> int:
        """Total number of images."""
        img_info = self._manifest.get("images", {})
        if isinstance(img_info, dict):
            return img_info.get("total", 0)
        return 0

    @property
    def created(self) -> Optional[str]:
        """Creation timestamp."""
        return self._manifest.get("created")

    @property
    def source(self) -> Optional[str]:
        """Original source path."""
        return self._manifest.get("source")

    # ========== Methods ==========

    def info(self) -> DatasetInfo:
        """
        Get detailed dataset information.

        Returns:
            DatasetInfo with all metadata

        Example:
            >>> dataset = Dataset.load("my-photos")
            >>> info = dataset.info()
            >>> print(f"Size: {info.size}")
            >>> print(f"Images: {info.total_images}")
        """
        # Count images in different locations
        train_dir = self._path / "train"
        valid_dir = self._path / "valid"
        unlabeled_dir = self._path / "images" / "unlabeled"

        train_count = sum(1 for _ in train_dir.glob("*.*")) if train_dir.exists() else 0
        valid_count = sum(1 for _ in valid_dir.glob("*.*")) if valid_dir.exists() else 0
        unlabeled_count = sum(1 for _ in unlabeled_dir.glob("*.*")) if unlabeled_dir.exists() else 0

        total = train_count + valid_count + unlabeled_count

        # Get size
        size_bytes = self._manifest.get("size_bytes", 0)
        if not size_bytes and self._path.exists():
            # Calculate if not in manifest
            size_bytes = sum(
                f.stat().st_size
                for f in self._path.rglob("*")
                if f.is_file()
            )

        return DatasetInfo(
            name=self.name,
            path=self._path,
            status=self.status,
            classes=self.classes,
            total_images=total,
            train_images=train_count,
            valid_images=valid_count,
            unlabeled_images=unlabeled_count,
            size_bytes=size_bytes,
            source=self.source
        )

    def delete(self, confirm: bool = False) -> None:
        """
        Delete this dataset.

        Args:
            confirm: Must be True to actually delete

        Example:
            >>> dataset = Dataset.load("my-photos")
            >>> dataset.delete(confirm=True)
        """
        if not confirm:
            raise ValueError(
                "Must pass confirm=True to delete dataset. "
                "This action cannot be undone."
            )

        from ..core.io import delete_tree
        delete_tree(self._path)

    def __repr__(self) -> str:
        return f"Dataset(name='{self.name}', images={self.images}, status='{self.status}')"

    def __str__(self) -> str:
        return self.name