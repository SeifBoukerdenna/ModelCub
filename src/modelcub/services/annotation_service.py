"""
Annotation service with ServiceResult pattern.

Handles YOLO format annotations (text files in labels/ directory).
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

from ..core.service_result import ServiceResult
from ..core.service_logging import log_service_call


@dataclass
class BoundingBox:
    """Bounding box in YOLO format (normalized 0-1)."""
    class_id: int
    x: float  # center x
    y: float  # center y
    w: float  # width
    h: float  # height

    def to_yolo_line(self) -> str:
        """Convert to YOLO format line."""
        return f"{self.class_id} {self.x:.6f} {self.y:.6f} {self.w:.6f} {self.h:.6f}"

    @classmethod
    def from_yolo_line(cls, line: str) -> BoundingBox:
        """Parse from YOLO format line."""
        parts = line.strip().split()
        return cls(
            class_id=int(parts[0]),
            x=float(parts[1]),
            y=float(parts[2]),
            w=float(parts[3]),
            h=float(parts[4])
        )


@dataclass
class SaveAnnotationRequest:
    """Request to save annotation."""
    dataset_name: str
    image_id: str
    boxes: List[BoundingBox]
    project_path: Path


@dataclass
class GetAnnotationRequest:
    """Request to get annotation(s)."""
    dataset_name: str
    image_id: Optional[str]
    project_path: Path


@dataclass
class DeleteAnnotationRequest:
    """Request to delete a specific box."""
    dataset_name: str
    image_id: str
    box_index: int
    project_path: Path


def _get_dataset_path(project_path: Path, dataset_name: str) -> Path:
    """Get dataset directory path."""
    return project_path / "data" / "datasets" / dataset_name


def _get_labels_dir(project_path: Path, dataset_name: str, split: str = "unlabeled") -> Path:
    """Get labels directory for a split."""
    return _get_dataset_path(project_path, dataset_name) / "labels" / split


def _get_images_dir(project_path: Path, dataset_name: str, split: str = "unlabeled") -> Path:
    """Get images directory for a split."""
    return _get_dataset_path(project_path, dataset_name) / "images" / split


def _find_image_split(project_path: Path, dataset_name: str, image_id: str) -> Optional[str]:
    """Find which split an image belongs to."""
    for split in ["train", "val", "test", "unlabeled"]:
        images_dir = _get_images_dir(project_path, dataset_name, split)
        if images_dir.exists():
            # Check for common image extensions
            for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                if (images_dir / f"{image_id}{ext}").exists():
                    return split
    return None


def _get_label_path(project_path: Path, dataset_name: str, image_id: str) -> Optional[Path]:
    """Get label file path for an image."""
    split = _find_image_split(project_path, dataset_name, image_id)
    if not split:
        return None

    labels_dir = _get_labels_dir(project_path, dataset_name, split)
    labels_dir.mkdir(parents=True, exist_ok=True)
    return labels_dir / f"{image_id}.txt"


@log_service_call("save_annotation")
def save_annotation(req: SaveAnnotationRequest) -> ServiceResult[Dict[str, Any]]:
    """
    Save annotation for an image.

    Args:
        req: Save annotation request

    Returns:
        ServiceResult with saved annotation data
    """
    try:
        label_path = _get_label_path(req.project_path, req.dataset_name, req.image_id)

        if not label_path:
            return ServiceResult.error(
                f"Image not found: {req.image_id}",
                code=2
            )

        # Write boxes to YOLO format
        lines = [box.to_yolo_line() for box in req.boxes]
        label_path.write_text("\n".join(lines) + "\n" if lines else "", encoding="utf-8")

        data = {
            "image_id": req.image_id,
            "num_boxes": len(req.boxes),
            "label_path": str(label_path)
        }

        return ServiceResult.ok(
            data=data,
            message=f"Saved {len(req.boxes)} box(es) for {req.image_id}"
        )

    except Exception as e:
        return ServiceResult.error(
            f"Failed to save annotation: {str(e)}",
            code=2
        )


@log_service_call("get_annotation")
def get_annotation(req: GetAnnotationRequest) -> ServiceResult[Dict[str, Any]]:
    """
    Get annotation(s) for image(s).

    Args:
        req: Get annotation request

    Returns:
        ServiceResult with annotation data
    """
    try:
        dataset_path = _get_dataset_path(req.project_path, req.dataset_name)

        if not dataset_path.exists():
            return ServiceResult.error(
                f"Dataset not found: {req.dataset_name}",
                code=2
            )

        # Single image
        if req.image_id:
            split = _find_image_split(req.project_path, req.dataset_name, req.image_id)
            if not split:
                return ServiceResult.error(
                    f"Image not found: {req.image_id}",
                    code=2
                )

            label_path = _get_label_path(req.project_path, req.dataset_name, req.image_id)
            boxes = []

            if label_path and label_path.exists():
                for line in label_path.read_text(encoding="utf-8").strip().split("\n"):
                    if line.strip():
                        box = BoundingBox.from_yolo_line(line)
                        boxes.append({
                            "class_id": box.class_id,
                            "x": box.x,
                            "y": box.y,
                            "w": box.w,
                            "h": box.h
                        })

            images_dir = _get_images_dir(req.project_path, req.dataset_name, split)

            # Find actual image file and return relative path
            image_path = None
            for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                candidate = images_dir / f"{req.image_id}{ext}"
                if candidate.exists():
                    # Return path relative to dataset root
                    image_path = f"images/{split}/{req.image_id}{ext}"
                    break

            data = {
                "image_id": req.image_id,
                "image_path": image_path,
                "split": split,
                "boxes": boxes,
                "num_boxes": len(boxes)
            }

            return ServiceResult.ok(
                data=data,
                message=json.dumps(data, indent=2)
            )

        # All images
        all_images = []
        for split in ["train", "val", "test", "unlabeled"]:
            images_dir = _get_images_dir(req.project_path, req.dataset_name, split)
            labels_dir = _get_labels_dir(req.project_path, req.dataset_name, split)

            if not images_dir.exists():
                continue

            for img_file in images_dir.iterdir():
                if img_file.suffix.lower() not in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                    continue

                image_id = img_file.stem
                label_path = labels_dir / f"{image_id}.txt"

                boxes = []
                if label_path.exists():
                    for line in label_path.read_text(encoding="utf-8").strip().split("\n"):
                        if line.strip():
                            box = BoundingBox.from_yolo_line(line)
                            boxes.append({
                                "class_id": box.class_id,
                                "x": box.x,
                                "y": box.y,
                                "w": box.w,
                                "h": box.h
                            })

                all_images.append({
                    "image_id": image_id,
                    "image_path": f"images/{split}/{img_file.name}",
                    "split": split,
                    "boxes": boxes,
                    "num_boxes": len(boxes)
                })

        data = {
            "images": all_images,
            "total": len(all_images)
        }

        return ServiceResult.ok(
            data=data,
            message=f"Found {len(all_images)} image(s)"
        )

    except Exception as e:
        return ServiceResult.error(
            f"Failed to get annotation: {str(e)}",
            code=2
        )


@log_service_call("delete_annotation")
def delete_annotation(req: DeleteAnnotationRequest) -> ServiceResult[Dict[str, Any]]:
    """
    Delete a specific bounding box from an annotation.

    Args:
        req: Delete annotation request

    Returns:
        ServiceResult with result data
    """
    try:
        label_path = _get_label_path(req.project_path, req.dataset_name, req.image_id)

        if not label_path or not label_path.exists():
            return ServiceResult.error(
                f"No annotation found for: {req.image_id}",
                code=2
            )

        # Read existing boxes
        lines = label_path.read_text(encoding="utf-8").strip().split("\n")
        boxes = [line for line in lines if line.strip()]

        if req.box_index < 0 or req.box_index >= len(boxes):
            return ServiceResult.error(
                f"Invalid box index: {req.box_index} (0-{len(boxes)-1})",
                code=2
            )

        # Remove box
        del boxes[req.box_index]

        # Write back
        if boxes:
            label_path.write_text("\n".join(boxes) + "\n", encoding="utf-8")
        else:
            # Delete empty label file
            label_path.unlink()

        data = {
            "image_id": req.image_id,
            "deleted_index": req.box_index,
            "remaining_boxes": len(boxes)
        }

        return ServiceResult.ok(
            data=data,
            message=f"Deleted box {req.box_index} from {req.image_id}"
        )

    except Exception as e:
        return ServiceResult.error(
            f"Failed to delete box: {str(e)}",
            code=2
        )


@log_service_call("get_annotation_stats")
def get_annotation_stats(dataset_name: str, project_path: Path) -> ServiceResult[Dict[str, Any]]:
    """
    Get annotation statistics for a dataset.

    Args:
        dataset_name: Dataset name
        project_path: Project root path

    Returns:
        ServiceResult with statistics
    """
    try:
        dataset_path = _get_dataset_path(project_path, dataset_name)

        if not dataset_path.exists():
            return ServiceResult.error(
                f"Dataset not found: {dataset_name}",
                code=2
            )

        total_images = 0
        labeled_images = 0
        total_boxes = 0

        for split in ["train", "val", "test", "unlabeled"]:
            images_dir = _get_images_dir(project_path, dataset_name, split)
            labels_dir = _get_labels_dir(project_path, dataset_name, split)

            if not images_dir.exists():
                continue

            for img_file in images_dir.iterdir():
                if img_file.suffix.lower() not in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                    continue

                total_images += 1

                label_path = labels_dir / f"{img_file.stem}.txt"
                if label_path.exists():
                    content = label_path.read_text(encoding="utf-8").strip()
                    if content:
                        labeled_images += 1
                        boxes = [line for line in content.split("\n") if line.strip()]
                        total_boxes += len(boxes)

        progress = labeled_images / total_images if total_images > 0 else 0.0

        data = {
            "total_images": total_images,
            "labeled": labeled_images,
            "unlabeled": total_images - labeled_images,
            "progress": progress,
            "total_boxes": total_boxes
        }

        return ServiceResult.ok(
            data=data,
            message=f"{labeled_images}/{total_images} labeled ({progress:.1%})"
        )

    except Exception as e:
        return ServiceResult.error(
            f"Failed to get stats: {str(e)}",
            code=2
        )