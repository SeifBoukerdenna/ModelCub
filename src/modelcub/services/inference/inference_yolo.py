"""
YOLO inference adapter for Ultralytics integration.

Handles YOLO-specific inference using the Ultralytics library.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import time
from .inference_base import (
    InferenceAdapter,
    ImagePrediction,
    Detection,
    BoundingBox
)


class YOLOInferenceAdapter(InferenceAdapter):
    """
    Inference adapter for YOLO models using Ultralytics.

    Supports YOLOv8, YOLOv9, YOLOv11 models.
    """

    def __init__(self):
        self.model = None
        self._class_names = []

    def load_model(self, model_path: Path, device: str = "cpu") -> None:
        """Load YOLO model from file."""
        try:
            from ultralytics import YOLO
        except ImportError:
            raise ImportError(
                "Ultralytics not installed. Install with: pip install ultralytics"
            )

        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")

        # Load model
        self.model = YOLO(str(model_path))

        # Set device
        self.model.to(device)

        # Extract class names
        if hasattr(self.model, 'names'):
            self._class_names = list(self.model.names.values())
        else:
            self._class_names = []

    def predict_image(
        self,
        image_path: Path,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        classes: Optional[List[int]] = None
    ) -> ImagePrediction:
        """Run inference on a single image."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Run inference
        start_time = time.time()
        results = self.model.predict(
            source=str(image_path),
            conf=conf_threshold,
            iou=iou_threshold,
            classes=classes,
            verbose=False
        )
        inference_time_ms = (time.time() - start_time) * 1000

        # Parse results
        result = results[0]  # Single image

        # Get image dimensions
        img_height, img_width = result.orig_shape

        # Extract detections
        detections = []
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes.cpu()

            for box in boxes:
                # Get box coordinates (x_center, y_center, width, height) normalized
                xywhn = box.xywhn[0].tolist()
                x_center, y_center, width, height = xywhn

                # Get class and confidence
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                class_name = self._class_names[class_id] if class_id < len(self._class_names) else str(class_id)

                detection = Detection(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    bbox=BoundingBox(
                        x=x_center,
                        y=y_center,
                        width=width,
                        height=height
                    )
                )
                detections.append(detection)

        return ImagePrediction(
            image_path=str(image_path),
            image_width=img_width,
            image_height=img_height,
            detections=detections,
            inference_time_ms=inference_time_ms
        )

    def predict_batch(
        self,
        image_paths: List[Path],
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        classes: Optional[List[int]] = None,
        batch_size: int = 16
    ) -> List[ImagePrediction]:
        """Run inference on multiple images."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Validate all images exist
        for img_path in image_paths:
            if not img_path.exists():
                raise FileNotFoundError(f"Image not found: {img_path}")

        predictions = []

        # Process in batches
        for i in range(0, len(image_paths), batch_size):
            batch_paths = image_paths[i:i + batch_size]

            # Run inference on batch
            start_time = time.time()
            results = self.model.predict(
                source=[str(p) for p in batch_paths],
                conf=conf_threshold,
                iou=iou_threshold,
                classes=classes,
                verbose=False
            )
            batch_time = (time.time() - start_time) * 1000
            avg_time_per_image = batch_time / len(batch_paths)

            # Parse each result
            for result, img_path in zip(results, batch_paths):
                img_height, img_width = result.orig_shape

                detections = []
                if result.boxes is not None and len(result.boxes) > 0:
                    boxes = result.boxes.cpu()

                    for box in boxes:
                        xywhn = box.xywhn[0].tolist()
                        x_center, y_center, width, height = xywhn

                        class_id = int(box.cls[0].item())
                        confidence = float(box.conf[0].item())
                        class_name = self._class_names[class_id] if class_id < len(self._class_names) else str(class_id)

                        detection = Detection(
                            class_id=class_id,
                            class_name=class_name,
                            confidence=confidence,
                            bbox=BoundingBox(
                                x=x_center,
                                y=y_center,
                                width=width,
                                height=height
                            )
                        )
                        detections.append(detection)

                prediction = ImagePrediction(
                    image_path=str(img_path),
                    image_width=img_width,
                    image_height=img_height,
                    detections=detections,
                    inference_time_ms=avg_time_per_image
                )
                predictions.append(prediction)

        return predictions

    def get_class_names(self) -> List[str]:
        """Get list of class names."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self._class_names.copy()

    def get_num_classes(self) -> int:
        """Get number of classes."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return len(self._class_names)

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None

    def save_annotations(
        self,
        predictions: List[ImagePrediction],
        output_dir: Path,
        save_images: bool = False,
        save_txt: bool = True
    ) -> None:
        """
        Save predictions in YOLO format.

        Args:
            predictions: List of predictions
            output_dir: Output directory
            save_images: Whether to save annotated images
            save_txt: Whether to save YOLO txt labels
        """
        output_dir = Path(output_dir)

        if save_txt:
            labels_dir = output_dir / "labels"
            labels_dir.mkdir(parents=True, exist_ok=True)

        if save_images:
            images_dir = output_dir / "images"
            images_dir.mkdir(parents=True, exist_ok=True)

        for pred in predictions:
            image_path = Path(pred.image_path)
            stem = image_path.stem

            # Save labels
            if save_txt:
                label_path = labels_dir / f"{stem}.txt"
                with open(label_path, 'w') as f:
                    for det in pred.detections:
                        # YOLO format: class x_center y_center width height
                        line = f"{det.class_id} {det.bbox.x} {det.bbox.y} {det.bbox.width} {det.bbox.height}\n"
                        f.write(line)

            # Save annotated image
            if save_images and self.is_loaded:
                # Use YOLO's built-in visualization
                result = self.model.predict(
                    source=str(image_path),
                    conf=0.25,  # Use stored detections, but need to re-run for visualization
                    verbose=False
                )[0]

                # Save annotated image
                annotated = result.plot()
                import cv2
                output_path = images_dir / f"{stem}.jpg"
                cv2.imwrite(str(output_path), annotated)