"""
ModelCub SDK - Dataset Management.

Provides high-level Python API for dataset operations.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import shutil
import json

from ..core.registries import DatasetRegistry
from ..core.paths import project_root


@dataclass
class DatasetInfo:
    """Dataset information."""
    name: str
    id: str
    path: Path
    images: int
    classes: List[str]
    status: str
    total_images: int
    size: str
    created: Optional[str] = None
    source: Optional[str] = None


@dataclass
class Box:
    """Bounding box in YOLO format (normalized 0-1)."""
    class_id: int
    x: float
    y: float
    w: float
    h: float

    def to_dict(self) -> Dict[str, Any]:
        return {"class_id": self.class_id, "x": self.x, "y": self.y, "w": self.w, "h": self.h}


class Dataset:
    """
    High-level interface for dataset operations.

    Example:
        >>> dataset = Dataset("my-dataset")
        >>> dataset.validate()
        >>> dataset.fix(auto=True)
    """

    def __init__(self, name: str, project_path: Optional[str | Path] = None):
        """
        Initialize Dataset.

        Args:
            name: Dataset name
            project_path: Project directory (searches upward if not provided)
        """
        self.name = name

        if project_path:
            self._project_path = Path(project_path).resolve()
        else:
            self._project_path = project_root()

        # Verify project exists
        if not (self._project_path / ".modelcub").exists():
            raise ValueError(f"Not a valid project: {self._project_path}")

        # Verify dataset exists
        registry = DatasetRegistry(self._project_path)
        self._data = registry.get_dataset(name)

        if not self._data:
            raise ValueError(f"Dataset not found: {name}")

        self._dataset_path = self._project_path / "data" / "datasets" / name

    # ========== Properties ==========

    @property
    def path(self) -> Path:
        """Dataset directory path."""
        return self._dataset_path

    @property
    def project_path(self) -> Path:
        """Parent project path."""
        return self._project_path

    @property
    def images(self) -> int:
        """Total number of images."""
        return self._data.get("num_images", 0)

    @property
    def status(self) -> str:
        """Dataset status."""
        return self._data.get("status", "ready")

    @property
    def size(self) -> str:
        # Calculate size
        size_bytes = 0
        try:
            for item in self._dataset_path.rglob("*"):
                if item.is_file():
                    size_bytes += item.stat().st_size
        except Exception:
            pass

        # Format size
        size_display = size_bytes
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_display < 1024:
                size_str = f"{size_display:.1f} {unit}"
                break
            size_display /= 1024
        else:
            size_str = f"{size_display:.1f} TB"


    def info(self) -> DatasetInfo:
        """
        Get dataset information.

        Returns:
            DatasetInfo object

        Example:
            >>> info = dataset.info()
            >>> print(info.total_images)
        """
        # Calculate size
        size_bytes = 0
        try:
            for item in self._dataset_path.rglob("*"):
                if item.is_file():
                    size_bytes += item.stat().st_size
        except Exception:
            pass

        # Format size
        size_display = size_bytes
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_display < 1024:
                size_str = f"{size_display:.1f} {unit}"
                break
            size_display /= 1024
        else:
            size_str = f"{size_display:.1f} TB"

        return DatasetInfo(
            name=self.name,
            id=self._data.get("id", self.name),
            path=self._dataset_path,
            images=self.images,
            classes=self.list_classes(),
            status=self.status,
            total_images=self.images,
            size=size_str,
            created=self._data.get("created"),
            source=self._data.get("source"),

        )

    # ========== Split Operations ==========

    def get_split_counts(self) -> Dict[str, int]:
        """
        Get image counts for each split.

        Returns:
            Dict with keys: train, val, test, unlabeled

        Example:
            >>> counts = dataset.get_split_counts()
            >>> print(f"Train: {counts['train']}")
        """
        splits = {}
        for split in ["train", "val", "test", "unlabeled"]:
            split_dir = self._dataset_path / "images" / split
            if split_dir.exists():
                splits[split] = sum(1 for _ in split_dir.glob("*.*"))
            else:
                splits[split] = 0
        return splits



    # ========== Dataset images ============

    def list_images(
        self,
        split: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        List images in this dataset.

        Args:
            split: Optional split filter ('train', 'val', 'test', 'unlabeled')
            limit: Max number of images to return
            offset: Offset for pagination

        Returns:
            Tuple of (image list, total count)

        Example:
            >>> images, total = dataset.list_images(split='train', limit=10)
            >>> print(f"Found {total} images, showing {len(images)}")
        """
        registry = DatasetRegistry(self._project_path)
        return registry.list_images(self.name, split, limit, offset)


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
        registry = DatasetRegistry(self._project_path)
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
        from ..core.exceptions import ClassExistsError

        registry = DatasetRegistry(self._project_path)

        try:
            assigned_id = registry.add_class(self.name, class_name, class_id)
            self.reload()  # Reload to get updated classes
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
        from ..core.exceptions import ClassNotFoundError

        registry = DatasetRegistry(self._project_path)

        try:
            registry.remove_class(self.name, class_name)
            self.reload()  # Reload metadata
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
        from ..core.exceptions import ClassNotFoundError, ClassExistsError

        registry = DatasetRegistry(self._project_path)

        try:
            registry.rename_class(self.name, old_name, new_name)
            self.reload()  # Reload metadata
        except (ClassNotFoundError, ClassExistsError) as e:
            raise ValueError(str(e))

    # ========== Validation & Fixing ==========

    def validate(self) -> Dict[str, Any]:
        """
        Validate dataset for issues.

        Returns:
            Validation report dictionary

        Example:
            >>> report = dataset.validate()
            >>> print(f"Health: {report['health_score']}/100")
        """
        # TODO: Implement validation logic
        raise NotImplementedError("Dataset validation not yet implemented")

    def fix(self, auto: bool = False) -> Dict[str, Any]:
        """
        Fix dataset issues.

        Args:
            auto: Automatically fix all issues

        Returns:
            Fix report dictionary

        Example:
            >>> report = dataset.fix(auto=True)
            >>> print(f"Fixed {report['total_fixed']} issues")
        """
        # TODO: Implement fix logic
        raise NotImplementedError("Dataset fixing not yet implemented")

    # ========== Version Control ==========

    def commit(self, message: str) -> str:
        """
        Commit dataset state (version control).

        Args:
            message: Commit message

        Returns:
            Commit ID

        Example:
            >>> commit_id = dataset.commit("Added 100 new images")
        """
        # TODO: Implement version control
        raise NotImplementedError("Dataset version control not yet implemented")

    def diff(self, version1: str, version2: str) -> Dict[str, Any]:
        """
        Compare two dataset versions.

        Args:
            version1: First version
            version2: Second version

        Returns:
            Diff report

        Example:
            >>> diff = dataset.diff("v1", "v2")
            >>> print(f"Added: {len(diff['added_images'])}")
        """
        # TODO: Implement diff
        raise NotImplementedError("Dataset diff not yet implemented")

    # ========== Dataset Operations ==========

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

        registry = DatasetRegistry(self._project_path)

        # Remove from registry
        registry.remove_dataset(self.name)

        # Delete directory
        if self._dataset_path.exists():
            shutil.rmtree(self._dataset_path)

    def reload(self) -> None:
        """
        Reload dataset metadata from registry.

        Example:
            >>> dataset.reload()
        """
        registry = DatasetRegistry(self._project_path)
        self._data = registry.get_dataset(self.name)

        if not self._data:
            raise ValueError(f"Dataset no longer exists: {self.name}")

    # ========== Annotation Operations ===========

    def get_annotation(self, image_id: str) -> Dict[str, Any]:
        """
        Get annotations for a specific image.

        Args:
            image_id: Image identifier

        Returns:
            Annotation data dictionary

        Raises:
            ValueError: If annotation retrieval fails
        """
        from ..services.annotation_service import get_annotation, GetAnnotationRequest

        req = GetAnnotationRequest(
            dataset_name=self.name,
            image_id=image_id,
            project_path=self._project_path
        )

        result = get_annotation(req)

        if not result.success:
            raise ValueError(f"Failed to get annotation: {result.message}")

        return result.data if result.data else {}

    def get_annotations(self) -> List[Dict[str, Any]]:
        """
        Get all annotations for this dataset.

        Returns:
            List of annotation dictionaries

        Raises:
            ValueError: If annotation retrieval fails
        """
        from ..services.annotation_service import get_annotation, GetAnnotationRequest

        req = GetAnnotationRequest(
            dataset_name=self.name,
            image_id=None,
            project_path=self._project_path
        )

        result = get_annotation(req)

        if not result.success:
            raise ValueError(f"Failed to get annotations: {result.message}")

        data = result.data if result.data else {}
        return data.get("images", [])

    def save_annotation(self, image_id: str, boxes: List[Box]) -> Dict[str, Any]:
        """
        Save annotations for an image.

        Args:
            image_id: Image identifier
            boxes: List of bounding boxes

        Returns:
            Result dictionary

        Raises:
            ValueError: If save fails
        """
        from ..services.annotation_service import (
            save_annotation, SaveAnnotationRequest, BoundingBox
        )

        bbox_list = [
            BoundingBox(
                class_id=b.class_id,
                x=b.x,
                y=b.y,
                w=b.w,
                h=b.h
            )
            for b in boxes
        ]

        req = SaveAnnotationRequest(
            dataset_name=self.name,
            image_id=image_id,
            boxes=bbox_list,
            project_path=self._project_path
        )

        result = save_annotation(req)

        if not result.success:
            raise ValueError(f"Failed to save annotation: {result.message}")

        return result.data if result.data else {}

    def delete_box(self, image_id: str, box_index: int) -> Dict[str, Any]:
        """
        Delete a specific bounding box from an image.

        Args:
            image_id: Image identifier
            box_index: Index of box to delete

        Returns:
            Result dictionary

        Raises:
            ValueError: If deletion fails
        """
        from ..services.annotation_service import delete_annotation, DeleteAnnotationRequest

        req = DeleteAnnotationRequest(
            dataset_name=self.name,
            image_id=image_id,
            box_index=box_index,
            project_path=self._project_path
        )

        result = delete_annotation(req)

        if not result.success:
            raise ValueError(f"Failed to delete box: {result.message}")

        return result.data if result.data else {}

    def annotation_stats(self) -> Dict[str, Any]:
        """
        Get annotation statistics for this dataset.

        Returns:
            Statistics dictionary

        Raises:
            ValueError: If stats retrieval fails
        """
        from ..services.annotation_service import get_annotation_stats

        result = get_annotation_stats(self.name, self._project_path)

        if not result.success:
            raise ValueError(f"Failed to get stats: {result.message}")

        return result.data if result.data else {}


    # ========== String Representations ==========

    def __repr__(self) -> str:
        return f"Dataset(name='{self.name}', images={self.images}, status='{self.status}')"

    def __str__(self) -> str:
        return f"Dataset: {self.name} ({self.images} images)"