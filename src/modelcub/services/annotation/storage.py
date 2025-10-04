# src/modelcub/services/annotation/storage.py
"""
Storage and persistence layer for annotations.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Optional

from .models import ImageAnnotation


class AnnotationStorage:
    """Handles loading and saving annotations to disk."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.annotations_file = self.output_dir / "annotations.json"

    def load_all(self) -> Dict[str, ImageAnnotation]:
        """Load all annotations from JSON file."""
        if not self.annotations_file.exists():
            return {}

        try:
            with open(self.annotations_file, 'r') as f:
                data = json.load(f)

            annotations = {}
            for img_id, img_data in data.items():
                annotations[img_id] = ImageAnnotation.from_dict(img_data)

            return annotations
        except Exception as e:
            print(f"Warning: Could not load annotations: {e}")
            return {}

    def save_all(self, annotations: Dict[str, ImageAnnotation]) -> None:
        """Save all annotations to JSON file."""
        data = {
            img_id: img_ann.to_dict()
            for img_id, img_ann in annotations.items()
        }

        with open(self.annotations_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get(self, image_id: str, annotations: Dict[str, ImageAnnotation]) -> Optional[ImageAnnotation]:
        """Get annotations for a specific image."""
        return annotations.get(image_id)

    def save_one(self, image_id: str, annotation: ImageAnnotation,
                 annotations: Dict[str, ImageAnnotation]) -> None:
        """Save annotation for a single image."""
        annotations[image_id] = annotation
        self.save_all(annotations)

    def delete_one(self, image_id: str, annotations: Dict[str, ImageAnnotation]) -> bool:
        """Delete annotations for a specific image."""
        if image_id in annotations:
            del annotations[image_id]
            self.save_all(annotations)
            return True
        return False