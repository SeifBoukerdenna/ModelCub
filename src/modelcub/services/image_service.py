"""
Image import service for ModelCub.
"""
from __future__ import annotations
import json
import shutil
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
import yaml

from ..core.images import scan_directory, format_size
from ..core.registries import DatasetRegistry


@dataclass
class ImportImagesRequest:
    """Request to import images into a dataset."""
    project_path: Path
    source: Path
    dataset_name: Optional[str] = None
    classes: Optional[List[str]] = None
    copy: bool = True
    validate: bool = True
    recursive: bool = False
    force: bool = False


@dataclass
class ImportImagesResult:
    """Result of image import operation."""
    success: bool
    message: str
    dataset_name: str
    dataset_path: Optional[Path] = None
    images_imported: int = 0


def _generate_dataset_id() -> str:
    """Generate unique dataset ID."""
    import hashlib
    import time
    return hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]


def _generate_dataset_name(source: Path) -> str:
    """Generate dataset name from source path."""
    base = source.name or "dataset"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{base}-{timestamp}"


def import_images(req: ImportImagesRequest) -> ImportImagesResult:
    """
    Import images from a directory into a dataset.

    Args:
        req: Import request parameters

    Returns:
        Import result with success status and details
    """
    # Validate source
    if not req.source.exists():
        return ImportImagesResult(
            success=False,
            message=f"Source directory not found: {req.source}",
            dataset_name=""
        )

    if not req.source.is_dir():
        return ImportImagesResult(
            success=False,
            message=f"Source must be a directory: {req.source}",
            dataset_name=""
        )

    # Scan for images
    scan_result = scan_directory(req.source, recursive=req.recursive)

    if scan_result.valid_count == 0:
        return ImportImagesResult(
            success=False,
            message="No valid images found in source directory",
            dataset_name=""
        )

    # Generate dataset name if not provided
    dataset_name = req.dataset_name or _generate_dataset_name(req.source)
    dataset_id = _generate_dataset_id()

    # Setup paths
    datasets_dir = req.project_path / "data" / "datasets"
    dataset_dir = datasets_dir / dataset_name
    unlabeled_dir = dataset_dir / "unlabeled"
    images_dir = unlabeled_dir / "images"

    # Check if dataset exists
    if dataset_dir.exists() and not req.force:
        return ImportImagesResult(
            success=False,
            message=f"Dataset already exists: {dataset_name}. Use --force to overwrite.",
            dataset_name=dataset_name
        )

    # Create directory structure
    images_dir.mkdir(parents=True, exist_ok=True)

    # Import images
    imported_count = 0
    total_size = 0

    for img_info in scan_result.valid:
        # Handle both Path objects and tuples/ImageInfo objects
        if isinstance(img_info, tuple):
            img_path = img_info[0]  # (path, ...)
        elif hasattr(img_info, 'path'):
            img_path = img_info.path
        else:
            img_path = img_info

        dest_path = images_dir / img_path.name

        # Handle duplicate filenames
        counter = 1
        while dest_path.exists():
            stem = img_path.stem
            suffix = img_path.suffix
            dest_path = images_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        try:
            if req.copy:
                shutil.copy2(img_path, dest_path)
            else:
                dest_path.symlink_to(img_path.absolute())

            imported_count += 1
            total_size += img_path.stat().st_size
        except Exception as e:
            continue

    # Parse classes
    classes = req.classes or []

    # Create manifest.json
    manifest = {
        "dataset": dataset_name,
        "id": dataset_id,
        "created": datetime.now().isoformat() + "Z",
        "source": str(req.source),
        "status": "unlabeled",
        "images": {
            "total": imported_count,
            "unlabeled": imported_count
        },
        "size_bytes": total_size,
        "classes": classes
    }

    manifest_path = dataset_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Create dataset.yaml (YOLO format)
    dataset_yaml = dataset_dir / "dataset.yaml"
    yaml_config = {
        "path": str(dataset_dir),
        "train": "train/images",
        "val": "val/images",
        "test": "test/images",
        "names": classes,
        "nc": len(classes)
    }

    with open(dataset_yaml, 'w') as f:
        yaml.safe_dump(yaml_config, f, default_flow_style=False, sort_keys=False)

    # Create import-info.json
    import_info = {
        "imported_at": datetime.now().isoformat() + "Z",
        "source": str(req.source),
        "recursive": req.recursive,
        "validated": req.validate,
        "method": "copy" if req.copy else "symlink",
        "images_found": scan_result.total_count,
        "images_valid": scan_result.valid_count,
        "images_invalid": scan_result.invalid_count,
        "images_imported": imported_count
    }

    import_info_path = dataset_dir / "import-info.json"
    with open(import_info_path, 'w') as f:
        json.dump(import_info, f, indent=2)

    # Register dataset
    registry = DatasetRegistry(req.project_path)
    registry.add_dataset({
        "id": dataset_id,
        "name": dataset_name,
        "created": manifest["created"],
        "status": "unlabeled",
        "num_images": imported_count,
        "images": {
            "total": imported_count,
            "unlabeled": imported_count
        },
        "classes": classes,
        "path": f"data/datasets/{dataset_name}",
        "source": str(req.source),
        "num_classes": len(classes)
    })

    registry.save()

    # Format message
    size_str = format_size(total_size)
    message = f"✅ Imported {imported_count} images into dataset '{dataset_name}'\n"
    message += f"   Path: {dataset_dir}\n"
    message += f"   Size: {size_str}\n"
    message += f"   Status: unlabeled"

    if classes:
        message += f"\n   Classes: {', '.join(classes)}"

    return ImportImagesResult(
        success=True,
        message=message,
        dataset_name=dataset_name,
        dataset_path=dataset_dir,
        images_imported=imported_count
    )