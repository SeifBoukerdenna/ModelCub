"""
Image import service for ModelCub.
"""
from __future__ import annotations
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..core.images import scan_directory, format_size, ImageInfo
from ..core.config import load_config
from ..core.registries import DatasetRegistry
from ..events import bus, DatasetImported


@dataclass
class ImportImagesRequest:
    """Request to import images into a dataset."""
    project_path: str | Path
    source: Path | str
    dataset_name: str | None = None
    copy: bool = True
    validate: bool = True
    recursive: bool = False
    force: bool = False


@dataclass
class ImportImagesResult:
    """Result of image import operation."""
    success: bool
    dataset_name: str
    dataset_path: Path
    image_count: int
    message: str
    dataset_id: str


def _sanitize_name(name: str) -> str:
    """Sanitize dataset name."""
    name = name.lower()
    name = "".join(c if c.isalnum() or c in "-_" else "-" for c in name)
    while "--" in name:
        name = name.replace("--", "-")
    return name.strip("-")


def _generate_dataset_name(source: Path, registry: DatasetRegistry) -> str:
    """Generate unique dataset name from source folder."""
    base_name = _sanitize_name(source.name)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    candidate = f"{base_name}-{timestamp}"

    counter = 2
    while registry.exists(candidate):
        candidate = f"{base_name}-{timestamp}-{counter}"
        counter += 1

    return candidate


def _generate_dataset_id() -> str:
    """Generate unique 8-character dataset ID."""
    import hashlib
    import time

    data = f"{time.time()}{id(object())}".encode()
    hash_hex = hashlib.sha256(data).hexdigest()
    return hash_hex[:8]


def _create_manifest(name: str, dataset_id: str, source: Path,
                     valid_images: list[ImageInfo], total_size: int) -> dict:
    """Create dataset manifest."""
    return {
        "dataset": name,
        "id": dataset_id,
        "created": datetime.utcnow().isoformat() + "Z",
        "source": str(source.resolve()),
        "status": "unlabeled",
        "images": {
            "total": len(valid_images),
            "unlabeled": len(valid_images)
        },
        "size_bytes": total_size,
        "classes": []
    }


def _copy_images(images: list[ImageInfo], dest_dir: Path) -> None:
    """Copy images to destination directory."""
    dest_dir.mkdir(parents=True, exist_ok=True)

    for img_info in images:
        dest_path = dest_dir / img_info.path.name

        # Handle name conflicts
        if dest_path.exists():
            stem = dest_path.stem
            suffix = dest_path.suffix
            counter = 2
            while dest_path.exists():
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        shutil.copy2(img_info.path, dest_path)


def _symlink_images(images: list[ImageInfo], dest_dir: Path) -> None:
    """Create symlinks to images."""
    dest_dir.mkdir(parents=True, exist_ok=True)

    for img_info in images:
        dest_path = dest_dir / img_info.path.name

        # Handle name conflicts
        if dest_path.exists():
            stem = dest_path.stem
            suffix = dest_path.suffix
            counter = 2
            while dest_path.exists():
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

        try:
            rel_source = img_info.path.resolve().relative_to(dest_dir.parent.parent)
            dest_path.symlink_to(f"../../{rel_source}")
        except (ValueError, OSError):
            dest_path.symlink_to(img_info.path.resolve())


def import_images(req: ImportImagesRequest) -> ImportImagesResult:
    """
    Import images from a folder into a ModelCub dataset.

    Args:
        req: Import request parameters

    Returns:
        ImportImagesResult with success status and details
    """
    # Resolve paths
    project_root = Path(req.project_path).resolve()
    source = Path(req.source).resolve()

    # Validate source
    if not source.exists():
        return ImportImagesResult(
            success=False,
            dataset_name="",
            dataset_path=Path(),
            image_count=0,
            message=f"Source directory not found: {source}",
            dataset_id=""
        )

    if not source.is_dir():
        return ImportImagesResult(
            success=False,
            dataset_name="",
            dataset_path=Path(),
            image_count=0,
            message=f"Source is not a directory: {source}",
            dataset_id=""
        )

    # Load project config and registry
    try:
        config = load_config(project_root)
        if not config:
            return ImportImagesResult(
                success=False,
                dataset_name="",
                dataset_path=Path(),
                image_count=0,
                message="Not in a ModelCub project. Run 'modelcub init' first.",
                dataset_id=""
            )

        registry = DatasetRegistry(project_root)
    except Exception as e:
        return ImportImagesResult(
            success=False,
            dataset_name="",
            dataset_path=Path(),
            image_count=0,
            message=f"Failed to load project: {e}",
            dataset_id=""
        )

    # Generate or validate name
    if req.dataset_name:
        name = _sanitize_name(req.dataset_name)
        if registry.exists(name) and not req.force:
            return ImportImagesResult(
                success=False,
                dataset_name=name,
                dataset_path=Path(),
                image_count=0,
                message=f"Dataset '{name}' already exists. Use force=True to overwrite.",
                dataset_id=""
            )
    else:
        name = _generate_dataset_name(source, registry)

    # Scan for images
    scan_result = scan_directory(source, recursive=req.recursive)

    if scan_result.valid_count == 0:
        return ImportImagesResult(
            success=False,
            dataset_name=name,
            dataset_path=Path(),
            image_count=0,
            message=f"No valid images found in {source}",
            dataset_id=""
        )

    # Generate dataset ID
    dataset_id = _generate_dataset_id()

    # Prepare dataset directory
    datasets_dir = project_root / config.paths.data / "datasets"
    dataset_path = datasets_dir / name
    images_dir = dataset_path / "images" / "unlabeled"

    # Create directory structure
    dataset_path.mkdir(parents=True, exist_ok=True)

    # Copy or symlink images
    try:
        if req.copy:
            _copy_images(scan_result.valid, images_dir)
        else:
            _symlink_images(scan_result.valid, images_dir)
    except Exception as e:
        return ImportImagesResult(
            success=False,
            dataset_name=name,
            dataset_path=dataset_path,
            image_count=0,
            message=f"Failed to import images: {e}",
            dataset_id=dataset_id
        )

    # Create manifest
    manifest = _create_manifest(
        name=name,
        dataset_id=dataset_id,
        source=source,
        valid_images=scan_result.valid,
        total_size=scan_result.total_size_bytes
    )

    manifest_path = dataset_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Create import info (provenance)
    import_info = {
        "source": str(source.resolve()),
        "imported_at": datetime.utcnow().isoformat() + "Z",
        "method": "copy" if req.copy else "symlink",
        "recursive": req.recursive,
        "original_count": scan_result.total_count,
        "imported_count": scan_result.valid_count,
        "skipped_count": scan_result.invalid_count
    }

    import_info_path = dataset_path / ".import-info.json"
    import_info_path.write_text(json.dumps(import_info, indent=2), encoding="utf-8")

    # Add to registry with correct image count
    registry_entry = {
        "id": dataset_id,
        "name": name,
        "created": manifest["created"],
        "status": "unlabeled",
        "num_images": scan_result.valid_count,  # CRITICAL: Store image count
        "images": {
            "total": scan_result.valid_count,
            "unlabeled": scan_result.valid_count
        },
        "classes": [],
        "path": str(dataset_path.relative_to(project_root)),
        "source": str(source)
    }

    registry.add_dataset(registry_entry)
    registry.save()  # Explicit save

    # Emit event
    bus.publish(DatasetImported(
        name=name,
        path=str(dataset_path),
        image_count=scan_result.valid_count,
        source=str(source)
    ))

    return ImportImagesResult(
        success=True,
        dataset_name=name,
        dataset_path=dataset_path,
        image_count=scan_result.valid_count,
        message=f"Successfully imported {scan_result.valid_count} images",
        dataset_id=dataset_id
    )