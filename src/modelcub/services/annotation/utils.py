# src/modelcub/services/annotation/utils.py
"""
Utility functions for annotation service.
"""
from __future__ import annotations
from typing import Tuple, List


def normalize_bbox(x1: float, y1: float, x2: float, y2: float) -> Tuple[float, float, float, float]:
    """
    Normalize bounding box coordinates to ensure top-left to bottom-right order.

    Args:
        x1, y1: First corner coordinates
        x2, y2: Second corner coordinates

    Returns:
        Normalized coordinates (x_min, y_min, x_max, y_max)
    """
    return (
        min(x1, x2),
        min(y1, y2),
        max(x1, x2),
        max(y1, y2)
    )


def bbox_to_yolo(x1: float, y1: float, x2: float, y2: float,
                 img_width: int, img_height: int) -> Tuple[float, float, float, float]:
    """
    Convert absolute bbox coordinates to YOLO format.

    Args:
        x1, y1: Top-left corner
        x2, y2: Bottom-right corner
        img_width: Image width
        img_height: Image height

    Returns:
        YOLO format (x_center, y_center, width, height) normalized to [0, 1]
    """
    x_center = (x1 + x2) / 2 / img_width
    y_center = (y1 + y2) / 2 / img_height
    width = abs(x2 - x1) / img_width
    height = abs(y2 - y1) / img_height

    return (x_center, y_center, width, height)


def yolo_to_bbox(x_center: float, y_center: float, width: float, height: float,
                 img_width: int, img_height: int) -> Tuple[float, float, float, float]:
    """
    Convert YOLO format to absolute bbox coordinates.

    Args:
        x_center, y_center: Center point (normalized)
        width, height: Box dimensions (normalized)
        img_width: Image width
        img_height: Image height

    Returns:
        Absolute coordinates (x1, y1, x2, y2)
    """
    w = width * img_width
    h = height * img_height
    x1 = (x_center * img_width) - (w / 2)
    y1 = (y_center * img_height) - (h / 2)
    x2 = x1 + w
    y2 = y1 + h

    return (x1, y1, x2, y2)


def calculate_iou(box1: List[List[float]], box2: List[List[float]]) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.

    Args:
        box1: [[x1, y1], [x2, y2]]
        box2: [[x1, y1], [x2, y2]]

    Returns:
        IoU score between 0 and 1
    """
    x1_1, y1_1 = box1[0]
    x2_1, y2_1 = box1[1]
    x1_2, y1_2 = box2[0]
    x2_2, y2_2 = box2[1]

    # Calculate intersection
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)

    if x2_i < x1_i or y2_i < y1_i:
        return 0.0

    intersection = (x2_i - x1_i) * (y2_i - y1_i)

    # Calculate union
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection

    return intersection / union if union > 0 else 0.0


def validate_bbox(points: List[List[float]], min_size: int = 10) -> bool:
    """
    Validate that a bounding box meets minimum size requirements.

    Args:
        points: [[x1, y1], [x2, y2]]
        min_size: Minimum width/height in pixels

    Returns:
        True if valid, False otherwise
    """
    if len(points) != 2:
        return False

    x1, y1 = points[0]
    x2, y2 = points[1]

    width = abs(x2 - x1)
    height = abs(y2 - y1)

    return width >= min_size and height >= min_size


def validate_polygon(points: List[List[float]], min_points: int = 3) -> bool:
    """
    Validate that a polygon has enough points.

    Args:
        points: List of [x, y] coordinates
        min_points: Minimum number of points

    Returns:
        True if valid, False otherwise
    """
    return len(points) >= min_points


def calculate_polygon_area(points: List[List[float]]) -> float:
    """
    Calculate area of a polygon using the shoelace formula.

    Args:
        points: List of [x, y] coordinates

    Returns:
        Area of the polygon
    """
    if len(points) < 3:
        return 0.0

    area = 0.0
    for i in range(len(points)):
        j = (i + 1) % len(points)
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]

    return abs(area) / 2.0


def point_in_bbox(x: float, y: float, bbox: List[List[float]]) -> bool:
    """
    Check if a point is inside a bounding box.

    Args:
        x, y: Point coordinates
        bbox: [[x1, y1], [x2, y2]]

    Returns:
        True if point is inside bbox
    """
    x1, y1 = bbox[0]
    x2, y2 = bbox[1]

    return x1 <= x <= x2 and y1 <= y <= y2


def generate_annotation_id() -> str:
    """
    Generate a unique annotation ID.

    Returns:
        Unique ID string
    """
    import time
    import random

    timestamp = int(time.time() * 1000)
    random_suffix = random.randint(1000, 9999)

    return f"ann_{timestamp}_{random_suffix}"


def sanitize_label(label: str) -> str:
    """
    Sanitize a label string for use in filenames and exports.

    Args:
        label: Raw label string

    Returns:
        Sanitized label
    """
    # Remove special characters, keep alphanumeric and underscores
    import re
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', label)

    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)

    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')

    return sanitized.lower()


def get_annotation_color(label: str, classes: List[str]) -> str:
    """
    Get a consistent color for a label.

    Args:
        label: Class label
        classes: List of all classes

    Returns:
        Hex color string
    """
    # Predefined colors for common classes
    color_palette = [
        '#6366f1',  # Blue
        '#10b981',  # Green
        '#f59e0b',  # Yellow
        '#ef4444',  # Red
        '#8b5cf6',  # Purple
        '#ec4899',  # Pink
        '#14b8a6',  # Teal
        '#f97316',  # Orange
    ]

    try:
        index = classes.index(label)
        return color_palette[index % len(color_palette)]
    except ValueError:
        return '#6366f1'  # Default blue