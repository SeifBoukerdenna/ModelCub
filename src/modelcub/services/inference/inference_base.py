"""
Base inference adapter interface.

Defines the contract for all inference adapters.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class BoundingBox:
    """Bounding box representation."""
    x: float  # x_center (normalized 0-1)
    y: float  # y_center (normalized 0-1)
    width: float  # width (normalized 0-1)
    height: float  # height (normalized 0-1)

    def to_xyxy(self, img_width: int, img_height: int) -> tuple:
        """Convert to absolute x1,y1,x2,y2 format."""
        x_center = self.x * img_width
        y_center = self.y * img_height
        w = self.width * img_width
        h = self.height * img_height

        x1 = x_center - w / 2
        y1 = y_center - h / 2
        x2 = x_center + w / 2
        y2 = y_center + h / 2

        return (x1, y1, x2, y2)

    def to_xywh(self, img_width: int, img_height: int) -> tuple:
        """Convert to absolute x,y,w,h format."""
        x = self.x * img_width
        y = self.y * img_height
        w = self.width * img_width
        h = self.height * img_height
        return (x, y, w, h)


@dataclass
class Detection:
    """Single detection result."""
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox


@dataclass
class ImagePrediction:
    """Prediction results for a single image."""
    image_path: str
    image_width: int
    image_height: int
    detections: List[Detection]
    inference_time_ms: float


class InferenceAdapter(ABC):
    """
    Abstract base class for inference adapters.

    All inference backends (YOLO, TensorFlow, PyTorch, etc.)
    must implement this interface.
    """

    @abstractmethod
    def load_model(self, model_path: Path, device: str = "cpu") -> None:
        """
        Load model from file.

        Args:
            model_path: Path to model file
            device: Device to run on (cpu, cuda, cuda:0, mps)

        Raises:
            FileNotFoundError: If model file not found
            ValueError: If model is invalid
        """
        pass

    @abstractmethod
    def predict_image(
        self,
        image_path: Path,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        classes: Optional[List[int]] = None
    ) -> ImagePrediction:
        """
        Run inference on a single image.

        Args:
            image_path: Path to image file
            conf_threshold: Confidence threshold (0-1)
            iou_threshold: IoU threshold for NMS (0-1)
            classes: Filter specific class IDs (None = all classes)

        Returns:
            ImagePrediction with detections
        """
        pass

    @abstractmethod
    def predict_batch(
        self,
        image_paths: List[Path],
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        classes: Optional[List[int]] = None,
        batch_size: int = 16
    ) -> List[ImagePrediction]:
        """
        Run inference on multiple images.

        Args:
            image_paths: List of image paths
            conf_threshold: Confidence threshold (0-1)
            iou_threshold: IoU threshold for NMS (0-1)
            classes: Filter specific class IDs (None = all classes)
            batch_size: Batch size for processing

        Returns:
            List of ImagePrediction results
        """
        pass

    @abstractmethod
    def get_class_names(self) -> List[str]:
        """
        Get list of class names from loaded model.

        Returns:
            List of class names
        """
        pass

    @abstractmethod
    def get_num_classes(self) -> int:
        """
        Get number of classes in loaded model.

        Returns:
            Number of classes
        """
        pass

    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        pass