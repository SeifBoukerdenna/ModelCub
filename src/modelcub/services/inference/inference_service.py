"""
Inference service for ModelCub.

Handles inference job creation, execution, and result management.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import yaml
import logging

logger = logging.getLogger(__name__)


class InferenceService:
    """
    Service for managing inference operations.

    Coordinates between adapters, registries, and file system.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.predictions_dir = self.project_root / "predictions"
        self.predictions_dir.mkdir(parents=True, exist_ok=True)

        # Import registries
        from ...core.registries import RunRegistry, ModelRegistry, InferenceRegistry

        self.run_registry = RunRegistry(project_root)
        self.model_registry = ModelRegistry(project_root)
        self.inference_registry = InferenceRegistry(project_root)

    def resolve_model_path(self, model_identifier: str) -> Path:
        """
        Resolve model identifier to actual model file path.

        Priority:
        1. Promoted model name → models/<name>/best.pt
        2. Run ID → runs/<run-id>/train/weights/best.pt
        3. Direct path → as-is

        Args:
            model_identifier: Model name, run ID, or path

        Returns:
            Path to model file

        Raises:
            FileNotFoundError: If model not found
        """
        # Check if it's a promoted model
        promoted = self.model_registry.get_model(model_identifier)
        if promoted:
            model_path = self.project_root / promoted['path']
            if model_path.exists():
                return model_path

        # Check if it's a run ID
        run = self.run_registry.get_run(model_identifier)
        if run:
            run_path = self.project_root / run['artifacts_path']
            weights_path = run_path / 'train' / 'weights' / 'best.pt'
            if weights_path.exists():
                return weights_path
            else:
                raise FileNotFoundError(
                    f"Best weights not found for run {model_identifier}: {weights_path}"
                )

        # Treat as direct path
        model_path = Path(model_identifier)
        if not model_path.is_absolute():
            model_path = self.project_root / model_path

        if model_path.exists():
            return model_path

        raise FileNotFoundError(
            f"Model not found: {model_identifier}\n"
            f"Tried: promoted model, run ID, and direct path"
        )

    def create_inference_job(
        self,
        model_identifier: str,
        input_type: str,
        input_path: str,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        device: str = "cpu",
        save_txt: bool = True,
        save_img: bool = False,
        classes: Optional[List[int]] = None,
        batch_size: int = 16
    ) -> str:
        """
        Create inference job.

        Args:
            model_identifier: Model name, run ID, or path
            input_type: Type of input (image, images, video, dataset)
            input_path: Path to input
            conf_threshold: Confidence threshold
            iou_threshold: IoU threshold
            device: Device (cpu, cuda, cuda:0, mps)
            save_txt: Save YOLO format labels
            save_img: Save annotated images
            classes: Filter specific classes
            batch_size: Batch size for processing

        Returns:
            Inference job ID
        """
        # Resolve model
        model_path = self.resolve_model_path(model_identifier)

        # Generate inference ID
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        inference_id = f"inf-{timestamp}"

        # Create output directory
        output_path = self.predictions_dir / inference_id
        output_path.mkdir(parents=True, exist_ok=True)

        # Create job info
        job_info = {
            'id': inference_id,
            'created': datetime.utcnow().isoformat() + 'Z',
            'model_source': model_identifier,
            'model_path': str(model_path.relative_to(self.project_root)),
            'input_type': input_type,
            'input_path': input_path,
            'output_path': str(output_path.relative_to(self.project_root)),
            'config': {
                'conf_threshold': conf_threshold,
                'iou_threshold': iou_threshold,
                'device': device,
                'save_txt': save_txt,
                'save_img': save_img,
                'classes': classes,
                'batch_size': batch_size
            },
            'status': 'pending',
            'stats': None
        }

        # Save config snapshot
        config_path = output_path / 'config.yaml'
        with open(config_path, 'w') as f:
            yaml.safe_dump(job_info, f, default_flow_style=False)

        # Register job
        self.inference_registry.add_inference(job_info)

        logger.info(f"Created inference job: {inference_id}")
        return inference_id

    def run_inference(
    self,
    inference_id: str,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
        """
        Execute inference job.

        Args:
            inference_id: Inference job ID
            progress_callback: Optional callback(current, total, message)

        Returns:
            Results dictionary with stats
        """
        from .inference_yolo import YOLOInferenceAdapter

        # Get job info
        job = self.inference_registry.get_inference(inference_id)
        if not job:
            raise ValueError(f"Inference job not found: {inference_id}")

        # Update status
        self.inference_registry.update_inference(inference_id, {'status': 'running'})

        try:
            # Load model
            model_path = self.project_root / job['model_path']
            adapter = YOLOInferenceAdapter()

            if progress_callback:
                progress_callback(0, 100, f"Loading model: {model_path.name}")

            adapter.load_model(
                model_path,
                device=job['config']['device']
            )

            # Collect images
            images = self._collect_images(job['input_type'], job['input_path'])

            if not images:
                raise ValueError(f"No images found in: {job['input_path']}")

            if progress_callback:
                progress_callback(10, 100, f"Found {len(images)} images")

            # Run predictions
            config = job['config']
            predictions = adapter.predict_batch(
                image_paths=images,
                conf_threshold=config['conf_threshold'],
                iou_threshold=config['iou_threshold'],
                classes=config['classes'],
                batch_size=config['batch_size']
            )

            if progress_callback:
                progress_callback(80, 100, "Processing results")

            # Save results - PASS THE ADAPTER! ✅
            output_path = self.project_root / job['output_path']
            self._save_results(predictions, output_path, config, adapter)  # ← CHANGED

            # Calculate stats
            total_detections = sum(len(p.detections) for p in predictions)
            avg_inference_time = sum(p.inference_time_ms for p in predictions) / len(predictions)

            stats = {
                'total_images': len(images),
                'total_detections': total_detections,
                'avg_inference_time_ms': round(avg_inference_time, 2),
                'classes_detected': list(set(
                    d.class_name for p in predictions for d in p.detections
                ))
            }

            # Update job
            self.inference_registry.update_inference(inference_id, {
                'status': 'completed',
                'stats': stats
            })

            if progress_callback:
                progress_callback(100, 100, "Complete")

            logger.info(f"Inference completed: {inference_id}")
            return stats

        except Exception as e:
            logger.error(f"Inference failed: {inference_id}: {e}")
            self.inference_registry.update_inference(inference_id, {
                'status': 'failed',
                'error': str(e)
            })
            raise


    def _collect_images(self, input_type: str, input_path: str) -> List[Path]:
        """Collect image paths based on input type."""
        images = []
        path = Path(input_path)

        if not path.is_absolute():
            path = self.project_root / path

        if input_type == 'image':
            # Single image
            if path.exists():
                images.append(path)

        elif input_type == 'images':
            # Directory of images
            if path.is_dir():
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.webp']:
                    images.extend(path.glob(ext))
                    images.extend(path.glob(ext.upper()))

        elif input_type == 'dataset':
            # Dataset directory (look for images in splits)
            for split in ['train', 'valid', 'test', 'val']:
                split_dir = path / split / 'images'
                if split_dir.exists():
                    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.webp']:
                        images.extend(split_dir.glob(ext))

        return sorted(images)

    def _save_results(
        self,
        predictions: List,
        output_path: Path,
        config: Dict,
        adapter  # ← ADDED PARAMETER
    ) -> None:
        """
        Save prediction results.

        Args:
            predictions: List of ImagePrediction objects
            output_path: Output directory path
            config: Configuration dictionary
            adapter: Loaded YOLOInferenceAdapter instance (for image visualization)
        """
        import json

        # Save JSON results
        results_json = {
            'predictions': [
                {
                    'image': p.image_path,
                    'width': p.image_width,
                    'height': p.image_height,
                    'inference_time_ms': p.inference_time_ms,
                    'detections': [
                        {
                            'class_id': d.class_id,
                            'class_name': d.class_name,
                            'confidence': d.confidence,
                            'bbox': {
                                'x': d.bbox.x,
                                'y': d.bbox.y,
                                'width': d.bbox.width,
                                'height': d.bbox.height
                            }
                        }
                        for d in p.detections
                    ]
                }
                for p in predictions
            ]
        }

        results_path = output_path / 'results.json'
        with open(results_path, 'w') as f:
            json.dump(results_json, f, indent=2)

        # Save labels/images if requested - USE THE PASSED ADAPTER! ✅
        if config['save_txt'] or config['save_img']:
            adapter.save_annotations(
                predictions=predictions,
                output_dir=output_path,
                save_images=config['save_img'],
                save_txt=config['save_txt']
            )

    def get_results(self, inference_id: str) -> Optional[Dict]:
        """Get inference results."""
        job = self.inference_registry.get_inference(inference_id)
        if not job:
            return None

        output_path = self.project_root / job['output_path']
        results_path = output_path / 'results.json'

        if results_path.exists():
            with open(results_path, 'r') as f:
                results = json.load(f)

            return {
                'job': job,
                'results': results
            }

        return {'job': job, 'results': None}

    def list_inferences(
        self,
        status: Optional[str] = None
    ) -> List[Dict]:
        """List inference jobs."""
        jobs = self.inference_registry.list_inferences()

        if status:
            jobs = [j for j in jobs if j.get('status') == status]

        return jobs