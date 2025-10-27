"""
Validation utilities for training prerequisites.

Checks GPU availability, disk space, dataset completeness before training.
"""
import shutil
import psutil
from pathlib import Path
from typing import Dict, List, Optional


class ValidationError(Exception):
    """Raised when validation fails."""
    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code


def validate_gpu(device: str) -> None:
    """
    Validate GPU is available if requested.

    Args:
        device: Device string (e.g., "cuda:0", "cpu")

    Raises:
        ValidationError: If GPU requested but not available
    """
    if device.startswith("cuda"):
        try:
            import torch
            if not torch.cuda.is_available():
                raise ValidationError(
                    "CUDA requested but no GPU available",
                    "TRAIN_DEVICE_UNAVAILABLE"
                )

            # Check specific device index
            if ":" in device:
                device_idx = int(device.split(":")[1])
                if device_idx >= torch.cuda.device_count():
                    raise ValidationError(
                        f"GPU {device_idx} not found. Available: {torch.cuda.device_count()}",
                        "TRAIN_DEVICE_UNAVAILABLE"
                    )
        except ImportError:
            raise ValidationError(
                "PyTorch not installed - cannot use CUDA",
                "TRAIN_DEVICE_UNAVAILABLE"
            )


def validate_disk_space(path: Path, required_gb: float = 5.0) -> None:
    """
    Validate sufficient disk space available.

    Args:
        path: Path to check (typically project root)
        required_gb: Minimum GB required

    Raises:
        ValidationError: If insufficient disk space
    """
    try:
        stat = shutil.disk_usage(path)
        available_gb = stat.free / (1024 ** 3)

        if available_gb < required_gb:
            raise ValidationError(
                f"Insufficient disk space: {available_gb:.1f}GB available, {required_gb}GB required",
                "TRAIN_DISK_LOW"
            )
    except ValidationError:
        # Re-raise ValidationError
        raise
    except Exception as e:
        # Don't fail validation if we can't check disk space (permissions, etc)
        pass


def validate_dataset_structure(dataset_path: Path) -> None:
    """
    Validate dataset has required structure.

    Args:
        dataset_path: Path to dataset directory

    Raises:
        ValidationError: If dataset structure invalid
    """
    # Check train split exists
    train_images = dataset_path / "train" / "images"
    if not train_images.exists():
        raise ValidationError(
            "Dataset missing train/images directory",
            "TRAIN_DATASET_NO_SPLITS"
        )

    # Check val split exists
    val_images = dataset_path / "val" / "images"
    if not val_images.exists():
        raise ValidationError(
            "Dataset missing val/images directory",
            "TRAIN_DATASET_NO_SPLITS"
        )


def validate_dataset_has_images(dataset_path: Path) -> Dict[str, int]:
    """
    Validate dataset has images and return counts.

    Args:
        dataset_path: Path to dataset directory

    Returns:
        Dictionary with image counts per split

    Raises:
        ValidationError: If no images found in training set
    """
    counts = {}

    for split in ["train", "val", "test"]:
        images_dir = dataset_path / split / "images"
        if images_dir.exists():
            count = sum(1 for f in images_dir.glob("*.*")
                       if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp'])
            counts[split] = count

    if counts.get("train", 0) == 0:
        raise ValidationError(
            "No images found in training set",
            "TRAIN_DATASET_NO_LABELS"
        )

    if counts.get("val", 0) == 0:
        raise ValidationError(
            "No images found in validation set",
            "TRAIN_DATASET_NO_LABELS"
        )

    return counts


def validate_dataset_yaml(dataset_path: Path) -> None:
    """
    Validate dataset.yaml exists and has required fields.

    Args:
        dataset_path: Path to dataset directory

    Raises:
        ValidationError: If dataset.yaml invalid
    """
    dataset_yaml = dataset_path / "dataset.yaml"
    if not dataset_yaml.exists():
        raise ValidationError(
            "dataset.yaml not found",
            "TRAIN_DATASET_INVALID"
        )

    import yaml
    try:
        with open(dataset_yaml, 'r') as f:
            data = yaml.safe_load(f)

        if not data:
            raise ValidationError(
                "dataset.yaml is empty",
                "TRAIN_DATASET_INVALID"
            )

        # Check for required fields
        if 'names' not in data and 'nc' not in data:
            raise ValidationError(
                "dataset.yaml missing 'names' or 'nc' field",
                "TRAIN_DATASET_INVALID"
            )

    except yaml.YAMLError as e:
        raise ValidationError(
            f"dataset.yaml parsing error: {e}",
            "TRAIN_DATASET_INVALID"
        )


def validate_model_name(model: str) -> None:
    """
    Validate model name is a known YOLO variant.

    Args:
        model: Model name (e.g., "yolov8n")

    Raises:
        ValidationError: If model name invalid
    """
    valid_models = [
        # YOLOv8
        "yolov8n", "yolov8s", "yolov8m", "yolov8l", "yolov8x",
        # YOLOv9
        "yolov9t", "yolov9s", "yolov9m", "yolov9c", "yolov9e",
        # YOLOv10
        "yolov10n", "yolov10s", "yolov10m", "yolov10b", "yolov10l", "yolov10x",
        # YOLOv11
        "yolov11n", "yolov11s", "yolov11m", "yolov11l", "yolov11x",
    ]

    # Also allow .pt files
    if model.endswith('.pt'):
        return

    if model not in valid_models:
        raise ValidationError(
            f"Unknown model: {model}. Valid models: {', '.join(valid_models[:5])}...",
            "TRAIN_MODEL_INVALID"
        )


def validate_all(
    dataset_path: Path,
    model: str,
    device: str,
    project_root: Path
) -> Dict[str, int]:
    """
    Run all validations before training.

    Args:
        dataset_path: Path to dataset
        model: Model name
        device: Training device
        project_root: Project root path

    Returns:
        Dictionary with image counts

    Raises:
        ValidationError: If any validation fails
    """
    validate_model_name(model)
    validate_gpu(device)
    validate_disk_space(project_root)
    validate_dataset_structure(dataset_path)
    validate_dataset_yaml(dataset_path)
    image_counts = validate_dataset_has_images(dataset_path)

    return image_counts