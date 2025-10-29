"""
ModelCub SDK - Promoted Model Management.

Provides high-level Python API for working with promoted models.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
import shutil


class InferenceResult:
    """
    Result from an inference operation.

    Attributes:
        inference_id: Unique inference job ID
        stats: Dictionary with inference statistics
        output_path: Path to inference results
        detections: List of detections (if available)
    """

    def __init__(self, inference_id: str, stats: Dict[str, Any], output_path: Path):
        self.inference_id = inference_id
        self.stats = stats
        self.output_path = output_path
        self._detections = None

    @property
    def total_images(self) -> int:
        """Total number of images processed."""
        return self.stats.get('total_images', 0)

    @property
    def total_detections(self) -> int:
        """Total number of detections found."""
        return self.stats.get('total_detections', 0)

    @property
    def avg_inference_time(self) -> float:
        """Average inference time in milliseconds."""
        return self.stats.get('avg_inference_time_ms', 0.0)

    @property
    def classes_detected(self) -> List[str]:
        """List of class names detected."""
        return self.stats.get('classes_detected', [])

    def __repr__(self) -> str:
        return (
            f"InferenceResult("
            f"images={self.total_images}, "
            f"detections={self.total_detections}, "
            f"time={self.avg_inference_time:.1f}ms)"
        )


class PromotedModel:
    """
    High-level interface for a promoted model.

    Example:
        >>> model = PromotedModel("detector-v1", project_path="/path/to/project")
        >>> print(f"Model: {model.name}")
        >>> print(f"mAP50: {model.map50}")
        >>> result = model.predict_image("test.jpg")
        >>> print(f"Found {result.total_detections} objects")
    """

    def __init__(self, name: str, project_path: str | Path):
        """
        Initialize PromotedModel.

        Args:
            name: Model name
            project_path: Project directory path
        """
        self.name = name
        self._project_path = Path(project_path).resolve()
        self._data = None
        self._load_data()

    def _load_data(self) -> None:
        """Load model data from registry."""
        from ..core.registries import ModelRegistry

        registry = ModelRegistry(self._project_path)
        self._data = registry.get_model(self.name)

        if self._data is None:
            raise ValueError(f"Model not found: {self.name}")

    # ========== Properties ==========

    @property
    def version(self) -> str:
        """Model version identifier."""
        return self._data['version']

    @property
    def run_id(self) -> str:
        """Training run that produced this model."""
        return self._data['run_id']

    @property
    def created(self) -> str:
        """ISO timestamp when model was promoted."""
        return self._data['created']

    @property
    def path(self) -> Path:
        """Path to model weights file."""
        return self._project_path / self._data['path']

    @property
    def metadata(self) -> Dict[str, Any]:
        """Model metadata (metrics, description, tags, etc.)."""
        return self._data['metadata'].copy()

    @property
    def description(self) -> str:
        """Model description."""
        return self.metadata.get('description', '')

    @property
    def tags(self) -> List[str]:
        """Model tags."""
        return self.metadata.get('tags', [])

    @property
    def metrics(self) -> Dict[str, Any]:
        """Training metrics."""
        return self.metadata.get('metrics', {})

    @property
    def config(self) -> Dict[str, Any]:
        """Training configuration used."""
        return self.metadata.get('config', {})

    @property
    def dataset_name(self) -> str:
        """Dataset used for training."""
        return self.metadata.get('dataset_name', '')

    @property
    def map50(self) -> Optional[float]:
        """mAP@0.5 metric if available."""
        return self.metrics.get('map50')

    @property
    def map50_95(self) -> Optional[float]:
        """mAP@0.5:0.95 metric if available."""
        return self.metrics.get('map50_95')

    # ========== Inference Methods ==========

    def predict_image(
        self,
        image_path: str | Path,
        conf: float = 0.25,
        iou: float = 0.45,
        device: str = "cpu",
        save_txt: bool = True,
        save_img: bool = False,
        classes: Optional[List[int]] = None,
        progress_callback: Optional[Callable] = None
    ) -> InferenceResult:
        """
        Run inference on a single image.

        Args:
            image_path: Path to image file
            conf: Confidence threshold (0-1)
            iou: IoU threshold for NMS (0-1)
            device: Device to use (cpu, cuda, cuda:0, mps)
            save_txt: Save YOLO format labels
            save_img: Save annotated image
            classes: Filter specific class IDs
            progress_callback: Optional callback(current, total, message)

        Returns:
            InferenceResult with statistics and output path

        Example:
            >>> result = model.predict_image("test.jpg", conf=0.5)
            >>> print(f"Found {result.total_detections} objects")
            >>> print(f"Results saved to: {result.output_path}")
        """
        from ..services.inference import InferenceService

        service = InferenceService(self._project_path)

        # Create inference job
        inference_id = service.create_inference_job(
            model_identifier=self.name,
            input_type='image',
            input_path=str(image_path),
            conf_threshold=conf,
            iou_threshold=iou,
            device=device,
            save_txt=save_txt,
            save_img=save_img,
            classes=classes
        )

        # Run inference
        stats = service.run_inference(inference_id, progress_callback=progress_callback)

        # Get output path
        job = service.inference_registry.get_inference(inference_id)
        output_path = self._project_path / job['output_path']

        return InferenceResult(inference_id, stats, output_path)

    def predict_images(
        self,
        directory: str | Path,
        conf: float = 0.25,
        iou: float = 0.45,
        device: str = "cpu",
        batch_size: int = 16,
        save_txt: bool = True,
        save_img: bool = False,
        classes: Optional[List[int]] = None,
        progress_callback: Optional[Callable] = None
    ) -> InferenceResult:
        """
        Run inference on a directory of images.

        Args:
            directory: Path to directory containing images
            conf: Confidence threshold (0-1)
            iou: IoU threshold for NMS (0-1)
            device: Device to use (cpu, cuda, cuda:0, mps)
            batch_size: Batch size for processing
            save_txt: Save YOLO format labels
            save_img: Save annotated images
            classes: Filter specific class IDs
            progress_callback: Optional callback(current, total, message)

        Returns:
            InferenceResult with statistics and output path

        Example:
            >>> result = model.predict_images("test_images/", batch_size=32)
            >>> print(f"Processed {result.total_images} images")
            >>> print(f"Found {result.total_detections} total detections")
        """
        from ..services.inference import InferenceService

        service = InferenceService(self._project_path)

        # Create inference job
        inference_id = service.create_inference_job(
            model_identifier=self.name,
            input_type='images',
            input_path=str(directory),
            conf_threshold=conf,
            iou_threshold=iou,
            device=device,
            save_txt=save_txt,
            save_img=save_img,
            classes=classes,
            batch_size=batch_size
        )

        # Run inference
        stats = service.run_inference(inference_id, progress_callback=progress_callback)

        # Get output path
        job = service.inference_registry.get_inference(inference_id)
        output_path = self._project_path / job['output_path']

        return InferenceResult(inference_id, stats, output_path)

    def predict_dataset(
        self,
        dataset_name: str,
        split: str = 'val',
        conf: float = 0.25,
        iou: float = 0.45,
        device: str = "cpu",
        batch_size: int = 16,
        save_txt: bool = True,
        save_img: bool = False,
        progress_callback: Optional[Callable] = None
    ) -> InferenceResult:
        """
        Run inference on a dataset split.

        Args:
            dataset_name: Name of dataset in project
            split: Dataset split (train, val, test)
            conf: Confidence threshold (0-1)
            iou: IoU threshold for NMS (0-1)
            device: Device to use (cpu, cuda, cuda:0, mps)
            batch_size: Batch size for processing
            save_txt: Save YOLO format labels
            save_img: Save annotated images
            progress_callback: Optional callback(current, total, message)

        Returns:
            InferenceResult with statistics and output path

        Example:
            >>> result = model.predict_dataset("my-dataset", split="test")
            >>> print(f"Processed {result.total_images} images")
            >>> print(f"Classes detected: {result.classes_detected}")
        """
        from ..services.inference import InferenceService
        from ..core.registries import DatasetRegistry

        # Validate dataset exists
        dataset_registry = DatasetRegistry(self._project_path)
        if not dataset_registry.exists(dataset_name):
            raise ValueError(f"Dataset not found: {dataset_name}")

        # Get dataset path
        dataset_path = self._project_path / "data" / "datasets" / dataset_name

        service = InferenceService(self._project_path)

        # Create inference job
        inference_id = service.create_inference_job(
            model_identifier=self.name,
            input_type='dataset',
            input_path=str(dataset_path),
            conf_threshold=conf,
            iou_threshold=iou,
            device=device,
            save_txt=save_txt,
            save_img=save_img,
            batch_size=batch_size
        )

        # Run inference
        stats = service.run_inference(inference_id, progress_callback=progress_callback)

        # Get output path
        job = service.inference_registry.get_inference(inference_id)
        output_path = self._project_path / job['output_path']

        return InferenceResult(inference_id, stats, output_path)

    # ========== Utility Methods ==========

    def info(self) -> None:
        """
        Print model information.

        Example:
            >>> model.info()
        """
        print(f"Model: {self.name}")
        print(f"Version: {self.version}")
        print(f"Created: {self.created}")
        print(f"Run: {self.run_id}")
        print(f"Path: {self.path}")
        print()

        if self.description:
            print(f"Description: {self.description}")
            print()

        if self.tags:
            print(f"Tags: {', '.join(self.tags)}")
            print()

        if self.metrics:
            print("Metrics:")
            for key, value in self.metrics.items():
                print(f"  {key}: {value}")
            print()

        if self.dataset_name:
            print(f"Dataset: {self.dataset_name}")

    def delete(self, force: bool = False) -> None:
        """
        Delete this promoted model.

        Args:
            force: Skip confirmation

        Example:
            >>> model.delete(force=True)
        """
        from ..core.registries import ModelRegistry

        if not force:
            response = input(f"Delete model '{self.name}'? (y/n): ")
            if response.lower() != 'y':
                print("Cancelled")
                return

        registry = ModelRegistry(self._project_path)
        registry.remove_model(self.name)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Returns:
            Dictionary with all model information

        Example:
            >>> data = model.to_dict()
            >>> print(data['version'])
        """
        return self._data.copy()

    def __repr__(self) -> str:
        """String representation."""
        return f"PromotedModel(name='{self.name}', version='{self.version}', run='{self.run_id}')"