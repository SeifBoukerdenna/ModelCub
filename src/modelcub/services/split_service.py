"""
Service for managing dataset splits.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import shutil

from ..core.service_result import ServiceResult
from ..core.service_logging import log_service_call


@log_service_call("move_to_split")
def move_to_split(
    project_path: Path,
    dataset_name: str,
    image_id: str,
    target_split: str
) -> ServiceResult[Dict[str, Any]]:
    """
    Move an image and its label from current split to target split.

    Args:
        project_path: Project root path
        dataset_name: Dataset name
        image_id: Image ID (without extension)
        target_split: Target split (train/val/test)

    Returns:
        ServiceResult with move details
    """
    try:
        dataset_path = project_path / "data" / "datasets" / dataset_name

        if not dataset_path.exists():
            return ServiceResult.error(f"Dataset not found: {dataset_name}", code=2)

        if target_split not in ["train", "val", "test"]:
            return ServiceResult.error(f"Invalid split: {target_split}", code=2)

        # Find current split
        current_split = None
        image_path = None

        for split in ["train", "val", "test", "unlabeled"]:
            images_dir = dataset_path / split / "images"
            if images_dir.exists():
                for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                    candidate = images_dir / f"{image_id}{ext}"
                    if candidate.exists():
                        current_split = split
                        image_path = candidate
                        break
                if image_path:
                    break

        if not image_path:
            return ServiceResult.error(f"Image not found: {image_id}", code=2)

        if current_split == target_split:
            return ServiceResult.ok(
                data={"image_id": image_id, "split": target_split},
                message=f"Image already in {target_split}"
            )

        # Setup target paths
        target_images_dir = dataset_path / target_split / "images"
        target_labels_dir = dataset_path / target_split / "labels"
        target_images_dir.mkdir(parents=True, exist_ok=True)
        target_labels_dir.mkdir(parents=True, exist_ok=True)

        # Move image
        target_image = target_images_dir / image_path.name
        shutil.move(str(image_path), str(target_image))

        # Move label if exists
        label_moved = False
        current_labels_dir = dataset_path / current_split / "labels"
        label_path = current_labels_dir / f"{image_id}.txt"

        if label_path.exists():
            target_label = target_labels_dir / f"{image_id}.txt"
            shutil.move(str(label_path), str(target_label))
            label_moved = True

        return ServiceResult.ok(
            data={
                "image_id": image_id,
                "from_split": current_split,
                "to_split": target_split,
                "label_moved": label_moved
            },
            message=f"Moved {image_id} from {current_split} to {target_split}"
        )

    except Exception as e:
        return ServiceResult.error(f"Failed to move image: {str(e)}", code=2)


@log_service_call("batch_move_to_splits")
def batch_move_to_splits(
    project_path: Path,
    dataset_name: str,
    assignments: List[Dict[str, str]]
) -> ServiceResult[Dict[str, Any]]:
    """
    Move multiple images to their assigned splits.

    Args:
        project_path: Project root path
        dataset_name: Dataset name
        assignments: List of {"image_id": str, "split": str}

    Returns:
        ServiceResult with batch move results
    """
    try:
        results = {"success": [], "failed": []}

        for assignment in assignments:
            image_id = assignment["image_id"]
            target_split = assignment["split"]

            result = move_to_split(project_path, dataset_name, image_id, target_split)

            if result.success:
                results["success"].append(image_id)
            else:
                results["failed"].append({"image_id": image_id, "error": result.message})

        return ServiceResult.ok(
            data=results,
            message=f"Moved {len(results['success'])}/{len(assignments)} images"
        )

    except Exception as e:
        return ServiceResult.error(f"Batch move failed: {str(e)}", code=2)