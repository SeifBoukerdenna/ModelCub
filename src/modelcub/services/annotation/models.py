# src/modelcub/services/annotation/models.py
"""
Data models for annotations.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Annotation:
    """Represents a single annotation (bounding box, polygon, etc.)"""
    id: str
    type: str  # 'bbox', 'polygon', 'point', 'line'
    label: str
    points: List[List[float]]  # [[x1,y1], [x2,y2], ...]
    confidence: float = 1.0
    metadata: Optional[Dict] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'type': self.type,
            'label': self.label,
            'points': self.points,
            'confidence': self.confidence,
            'metadata': self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: dict) -> Annotation:
        """Create from dictionary."""
        return cls(
            id=data['id'],
            type=data['type'],
            label=data['label'],
            points=data['points'],
            confidence=data.get('confidence', 1.0),
            metadata=data.get('metadata')
        )


@dataclass
class ImageAnnotation:
    """Complete annotation for an image"""
    image_path: str
    image_id: str
    width: int
    height: int
    annotations: List[Annotation]
    timestamp: str
    annotator: str = "modelcub"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'image_path': self.image_path,
            'image_id': self.image_id,
            'width': self.width,
            'height': self.height,
            'timestamp': self.timestamp,
            'annotator': self.annotator,
            'annotations': [ann.to_dict() for ann in self.annotations]
        }

    @classmethod
    def from_dict(cls, data: dict) -> ImageAnnotation:
        """Create from dictionary."""
        ann_objects = [
            Annotation.from_dict(ann)
            for ann in data.get('annotations', [])
        ]

        return cls(
            image_path=data['image_path'],
            image_id=data['image_id'],
            width=data['width'],
            height=data['height'],
            annotations=ann_objects,
            timestamp=data['timestamp'],
            annotator=data.get('annotator', 'modelcub')
        )


@dataclass
class ImageInfo:
    """Information about an image in the dataset."""
    id: str
    path: str
    name: str
    relative_path: str
    has_annotations: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'path': self.path,
            'name': self.name,
            'relative_path': self.relative_path,
            'has_annotations': self.has_annotations
        }