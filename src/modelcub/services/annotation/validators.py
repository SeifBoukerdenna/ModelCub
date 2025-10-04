# src/modelcub/services/annotation/validators.py
"""
Validation logic for annotations.
"""
from __future__ import annotations
from typing import List, Optional, Tuple

from .models import Annotation, ImageAnnotation


class AnnotationValidator:
    """Validates annotations for correctness and quality."""

    def __init__(self, classes: List[str], min_bbox_size: int = 10):
        self.classes = classes
        self.min_bbox_size = min_bbox_size

    def validate_annotation(self, annotation: Annotation) -> Tuple[bool, Optional[str]]:
        """
        Validate a single annotation.

        Args:
            annotation: Annotation to validate

        Returns:
            (is_valid, error_message)
        """
        # Check label is in classes
        if annotation.label not in self.classes:
            return False, f"Invalid label '{annotation.label}'. Must be one of: {self.classes}"

        # Check annotation type
        if annotation.type not in ['bbox', 'polygon', 'point', 'line']:
            return False, f"Invalid annotation type: {annotation.type}"

        # Type-specific validation
        if annotation.type == 'bbox':
            return self._validate_bbox(annotation)
        elif annotation.type == 'polygon':
            return self._validate_polygon(annotation)
        elif annotation.type == 'point':
            return self._validate_point(annotation)
        elif annotation.type == 'line':
            return self._validate_line(annotation)

        return True, None

    def _validate_bbox(self, annotation: Annotation) -> Tuple[bool, Optional[str]]:
        """Validate bounding box annotation."""
        if len(annotation.points) != 2:
            return False, "Bounding box must have exactly 2 points"

        x1, y1 = annotation.points[0]
        x2, y2 = annotation.points[1]

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if width < self.min_bbox_size or height < self.min_bbox_size:
            return False, f"Bounding box too small (min size: {self.min_bbox_size}px)"

        return True, None

    def _validate_polygon(self, annotation: Annotation) -> Tuple[bool, Optional[str]]:
        """Validate polygon annotation."""
        if len(annotation.points) < 3:
            return False, "Polygon must have at least 3 points"

        # Check for self-intersection (basic check)
        if self._has_self_intersection(annotation.points):
            return False, "Polygon has self-intersection"

        return True, None

    def _validate_point(self, annotation: Annotation) -> Tuple[bool, Optional[str]]:
        """Validate point annotation."""
        if len(annotation.points) != 1:
            return False, "Point annotation must have exactly 1 point"

        return True, None

    def _validate_line(self, annotation: Annotation) -> Tuple[bool, Optional[str]]:
        """Validate line annotation."""
        if len(annotation.points) < 2:
            return False, "Line annotation must have at least 2 points"

        return True, None

    def _has_self_intersection(self, points: List[List[float]]) -> bool:
        """
        Check if a polygon has self-intersections (simplified check).

        Args:
            points: Polygon points

        Returns:
            True if self-intersection detected
        """
        # Simplified check - just verify no adjacent edges are identical
        n = len(points)
        for i in range(n):
            j = (i + 1) % n
            if points[i] == points[j]:
                return True

        return False

    def validate_image_annotation(self, img_ann: ImageAnnotation) -> Tuple[bool, List[str]]:
        """
        Validate all annotations for an image.

        Args:
            img_ann: Image annotation to validate

        Returns:
            (all_valid, list_of_errors)
        """
        errors = []

        # Validate image dimensions
        if img_ann.width <= 0 or img_ann.height <= 0:
            errors.append(f"Invalid image dimensions: {img_ann.width}x{img_ann.height}")

        # Validate each annotation
        for i, ann in enumerate(img_ann.annotations):
            valid, error = self.validate_annotation(ann)
            if not valid:
                errors.append(f"Annotation {i} ({ann.id}): {error}")

            # Check if annotation is within image bounds
            if not self._is_within_bounds(ann, img_ann.width, img_ann.height):
                errors.append(f"Annotation {i} ({ann.id}) is outside image bounds")

        return len(errors) == 0, errors

    def _is_within_bounds(self, annotation: Annotation, width: int, height: int) -> bool:
        """Check if annotation is within image bounds."""
        for point in annotation.points:
            x, y = point
            if x < 0 or x > width or y < 0 or y > height:
                return False
        return True

    def check_duplicates(self, annotations: List[Annotation],
                        iou_threshold: float = 0.95) -> List[Tuple[int, int]]:
        """
        Find potential duplicate annotations.

        Args:
            annotations: List of annotations
            iou_threshold: IoU threshold for considering duplicates

        Returns:
            List of (index1, index2) pairs of potential duplicates
        """
        from .utils import calculate_iou

        duplicates = []

        for i in range(len(annotations)):
            for j in range(i + 1, len(annotations)):
                ann1, ann2 = annotations[i], annotations[j]

                # Only check same type and label
                if ann1.type != ann2.type or ann1.label != ann2.label:
                    continue

                if ann1.type == 'bbox':
                    iou = calculate_iou(ann1.points, ann2.points)
                    if iou >= iou_threshold:
                        duplicates.append((i, j))

        return duplicates

    def suggest_corrections(self, annotation: Annotation) -> List[str]:
        """
        Suggest corrections for an annotation.

        Args:
            annotation: Annotation to analyze

        Returns:
            List of suggestions
        """
        suggestions = []

        if annotation.type == 'bbox':
            x1, y1 = annotation.points[0]
            x2, y2 = annotation.points[1]

            width = abs(x2 - x1)
            height = abs(y2 - y1)

            # Check aspect ratio
            aspect_ratio = width / height if height > 0 else 0
            if aspect_ratio > 10 or aspect_ratio < 0.1:
                suggestions.append(f"Unusual aspect ratio: {aspect_ratio:.2f}")

            # Check size
            if width < 20 or height < 20:
                suggestions.append("Very small bounding box - consider reviewing")

        elif annotation.type == 'polygon':
            if len(annotation.points) > 50:
                suggestions.append("Polygon has many points - consider simplifying")

        # Check confidence
        if annotation.confidence < 0.5:
            suggestions.append(f"Low confidence score: {annotation.confidence:.2f}")

        return suggestions