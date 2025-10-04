# src/modelcub/services/annotation/image_handler.py
"""
Image discovery and management.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict

from .models import ImageInfo, ImageAnnotation


class ImageHandler:
    """Handles image discovery and metadata."""

    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir).resolve()

    def discover_images(self, annotations: Dict[str, ImageAnnotation]) -> List[ImageInfo]:
        """
        Find all images in data directory and subdirectories.

        Args:
            annotations: Current annotations dict to check if images are annotated

        Returns:
            List of ImageInfo objects
        """
        images = []

        print(f"Searching for images in: {self.data_dir}")

        for img_path in sorted(self.data_dir.rglob('*')):
            if not img_path.is_file():
                continue

            if img_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            rel_path = img_path.relative_to(self.data_dir)
            img_id = str(rel_path).replace('\\', '/')

            image_info = ImageInfo(
                id=img_id,
                path=str(img_path.resolve()),
                name=img_path.name,
                relative_path=str(rel_path),
                has_annotations=img_id in annotations
            )

            images.append(image_info)

        print(f"Found {len(images)} images")
        if images:
            print(f"First image: {images[0].path}")

        return images

    def find_image_by_id(self, image_id: str, images: List[ImageInfo]) -> ImageInfo | None:
        """Find an image by its ID."""
        for img in images:
            if img.id == image_id:
                return img
        return None

    def update_annotation_status(self, image_id: str, has_annotations: bool,
                                images: List[ImageInfo]) -> None:
        """Update the annotation status of an image."""
        for img in images:
            if img.id == image_id:
                img.has_annotations = has_annotations
                break