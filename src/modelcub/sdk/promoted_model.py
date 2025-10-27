"""
ModelCub SDK - Promoted Model Management.

Provides high-level Python API for working with promoted models.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any, List
import shutil


class PromotedModel:
    """
    High-level interface for a promoted model.

    Example:
        >>> model = PromotedModel("detector-v1", project_path="/path/to/project")
        >>> print(f"Model: {model.name}")
        >>> print(f"mAP50: {model.metadata.get('metrics', {}).get('map50')}")
        >>> predictions = model.predict("image.jpg")
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

    # ========== Methods ==========

    def reload(self) -> None:
        """
        Reload model data from registry.

        Example:
            >>> model.reload()
        """
        self._load_data()

    def predict(
        self,
        source: str | Path,
        conf: float = 0.25,
        iou: float = 0.7,
        imgsz: int = 640,
        save: bool = False,
        save_txt: bool = False,
        save_conf: bool = False,
        **kwargs
    ) -> Any:
        """
        Run inference on image(s), video, or directory.

        Args:
            source: Path to image, video, directory, or URL
            conf: Confidence threshold
            iou: IoU threshold for NMS
            imgsz: Input image size
            save: Save images with predictions
            save_txt: Save results as txt files
            save_conf: Save confidence in txt files
            **kwargs: Additional YOLO predict parameters

        Returns:
            YOLO Results object(s)

        Example:
            >>> results = model.predict("image.jpg")
            >>> results = model.predict("images/", save=True)
            >>> for r in results:
            ...     print(r.boxes)
        """
        from ultralytics import YOLO

        yolo_model = YOLO(str(self.path))

        return yolo_model.predict(
            source=str(source),
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            save=save,
            save_txt=save_txt,
            save_conf=save_conf,
            **kwargs
        )

    def export(
        self,
        format: str = 'onnx',
        imgsz: int = 640,
        output: Optional[str | Path] = None,
        **kwargs
    ) -> Path:
        """
        Export model to different format.

        Args:
            format: Export format (onnx, torchscript, openvino, engine, coreml, etc.)
            imgsz: Input image size
            output: Output path (default: auto-generated)
            **kwargs: Additional YOLO export parameters

        Returns:
            Path to exported model

        Example:
            >>> model.export(format='onnx')
            >>> model.export(format='engine', output='model.trt')
        """
        from ultralytics import YOLO

        yolo_model = YOLO(str(self.path))

        # Export
        export_path = yolo_model.export(
            format=format,
            imgsz=imgsz,
            **kwargs
        )

        # Move to desired location if specified
        if output:
            output_path = Path(output).resolve()
            shutil.move(str(export_path), str(output_path))
            return output_path

        return Path(export_path)

    def evaluate(
        self,
        data: Optional[str | Path] = None,
        split: str = 'val',
        imgsz: int = 640,
        batch: int = 16,
        **kwargs
    ) -> Any:
        """
        Evaluate model on dataset.

        Args:
            data: Path to dataset YAML (default: use original training dataset)
            split: Dataset split to evaluate on ('val', 'test')
            imgsz: Input image size
            batch: Batch size
            **kwargs: Additional YOLO val parameters

        Returns:
            YOLO validation results

        Example:
            >>> results = model.evaluate()
            >>> print(f"mAP50: {results.box.map50}")
        """
        from ultralytics import YOLO

        yolo_model = YOLO(str(self.path))

        # If no data provided, try to construct from metadata
        if data is None and self.dataset_name:
            dataset_path = self._project_path / "data" / "datasets" / self.dataset_name
            data_yaml = dataset_path / "data.yaml"
            if data_yaml.exists():
                data = str(data_yaml)

        return yolo_model.val(
            data=data,
            split=split,
            imgsz=imgsz,
            batch=batch,
            **kwargs
        )

    def info(self) -> None:
        """
        Print detailed model information.

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