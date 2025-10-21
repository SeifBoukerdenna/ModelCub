"""
Service for managing dataset splits.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import shutil
import random

from ..core.service_result import ServiceResult
from ..core.service_logging import log_service_call


@log_service_call("move_to_split")
def move_to_split(
    project_path: Path,
    dataset_name: str,
    image_id: str,
    target_split: str
) -> ServiceResult[Dict[str, Any]]:
    """Move an image and its label from current split to target split."""
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
    """Move multiple images to their assigned splits."""
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


@log_service_call("auto_split_by_percentage")
def auto_split_by_percentage(
    project_path: Path,
    dataset_name: str,
    train_pct: float = 70.0,
    val_pct: float = 20.0,
    test_pct: float = 10.0,
    source_split: str = "unlabeled",
    shuffle: bool = True,
    seed: int = 42
) -> ServiceResult[Dict[str, Any]]:
    """
    Automatically split images by percentage from a source split.

    Args:
        project_path: Project root path
        dataset_name: Dataset name
        train_pct: Training percentage (default 70)
        val_pct: Validation percentage (default 20)
        test_pct: Test percentage (default 10)
        source_split: Source split to redistribute from (default "unlabeled")
        shuffle: Whether to shuffle before splitting (default True)
        seed: Random seed for reproducibility (default 42)

    Returns:
        ServiceResult with split statistics
    """
    try:
        # Validate percentages
        total_pct = train_pct + val_pct + test_pct
        if abs(total_pct - 100.0) > 0.01:
            return ServiceResult.error(
                f"Percentages must sum to 100 (got {total_pct})",
                code=2
            )

        dataset_path = project_path / "data" / "datasets" / dataset_name
        if not dataset_path.exists():
            return ServiceResult.error(f"Dataset not found: {dataset_name}", code=2)

        # Get all images from source split
        source_images_dir = dataset_path / source_split / "images"
        if not source_images_dir.exists():
            return ServiceResult.error(
                f"Source split '{source_split}' not found",
                code=2
            )

        # Collect all image files
        image_files = []
        for ext in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
            image_files.extend(source_images_dir.glob(f"*{ext}"))

        if not image_files:
            return ServiceResult.error(
                f"No images found in {source_split} split",
                code=2
            )

        # Shuffle if requested
        if shuffle:
            random.seed(seed)
            random.shuffle(image_files)

        # Calculate split counts
        total = len(image_files)
        train_count = int(total * train_pct / 100)
        val_count = int(total * val_pct / 100)
        # Remaining goes to test to avoid rounding issues
        test_count = total - train_count - val_count

        # Create assignments
        assignments = []
        for i, img_path in enumerate(image_files):
            image_id = img_path.stem

            if i < train_count:
                split = "train"
            elif i < train_count + val_count:
                split = "val"
            else:
                split = "test"

            assignments.append({"image_id": image_id, "split": split})

        # Perform batch move
        result = batch_move_to_splits(project_path, dataset_name, assignments)

        if result.success:
            result.data["distribution"] = {
                "train": train_count,
                "val": val_count,
                "test": test_count,
                "total": total
            }
            result.message = (
                f"Split {total} images: "
                f"{train_count} train ({train_pct}%), "
                f"{val_count} val ({val_pct}%), "
                f"{test_count} test ({test_pct}%)"
            )

        return result

    except Exception as e:
        return ServiceResult.error(f"Auto-split failed: {str(e)}", code=2)