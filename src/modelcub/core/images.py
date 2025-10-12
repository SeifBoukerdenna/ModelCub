"""
Core image validation and scanning utilities.
"""
from __future__ import annotations
from pathlib import Path
from typing import NamedTuple
from dataclasses import dataclass


# Supported image extensions
VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}


class ImageInfo(NamedTuple):
    """Information about a single image."""
    path: Path
    size_bytes: int
    width: int
    height: int
    format: str


@dataclass
class ScanResult:
    """Result of scanning a directory for images."""
    valid: list[ImageInfo]
    invalid: list[tuple[Path, str]]  # (path, error_message)
    total_size_bytes: int

    @property
    def valid_count(self) -> int:
        return len(self.valid)

    @property
    def invalid_count(self) -> int:
        return len(self.invalid)

    @property
    def total_count(self) -> int:
        return self.valid_count + self.invalid_count


def is_image_file(path: Path) -> bool:
    """Check if file has valid image extension."""
    return path.suffix.lower() in VALID_IMAGE_EXTENSIONS


def validate_image(path: Path) -> ImageInfo | str:
    """
    Validate a single image file.

    Returns:
        ImageInfo if valid, error message string if invalid
    """
    try:
        from PIL import Image

        if not path.exists():
            return "File not found"

        if not path.is_file():
            return "Not a file"

        # Try to open and validate
        with Image.open(path) as img:
            # Force load to catch corrupt files
            img.verify()

        # Reopen to get info (verify closes the file)
        with Image.open(path) as img:
            width, height = img.size
            format_name = img.format or "unknown"

        size_bytes = path.stat().st_size

        return ImageInfo(
            path=path,
            size_bytes=size_bytes,
            width=width,
            height=height,
            format=format_name
        )

    except ImportError:
        return "PIL/Pillow not installed"
    except Exception as e:
        return f"Invalid image: {type(e).__name__}"


def scan_directory(source: Path, recursive: bool = False) -> ScanResult:
    """
    Scan directory for valid images.

    Args:
        source: Directory to scan
        recursive: Search subdirectories

    Returns:
        ScanResult with valid and invalid images
    """
    valid: list[ImageInfo] = []
    invalid: list[tuple[Path, str]] = []
    total_size = 0

    if not source.exists():
        return ScanResult(valid=[], invalid=[], total_size_bytes=0)

    # Find all potential image files
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"

    for path in source.glob(pattern):
        if not path.is_file():
            continue

        if not is_image_file(path):
            continue

        result = validate_image(path)

        if isinstance(result, ImageInfo):
            valid.append(result)
            total_size += result.size_bytes
        else:
            invalid.append((path, result))

    return ScanResult(
        valid=valid,
        invalid=invalid,
        total_size_bytes=total_size
    )


def format_size(bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"