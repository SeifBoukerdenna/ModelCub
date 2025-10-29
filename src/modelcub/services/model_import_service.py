"""
Model import service for ModelCub.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import shutil
import logging

logger = logging.getLogger(__name__)


class ModelImportService:
    """
    Service for importing external models into ModelCub.

    Handles validation, metadata extraction, and registration.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.models_dir = project_root / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def validate_model_file(self, model_path: Path) -> Dict[str, Any]:
        """
        Validate model file and extract metadata.

        Args:
            model_path: Path to model file

        Returns:
            Dictionary with model metadata

        Raises:
            ValueError: If model is invalid
            FileNotFoundError: If model file doesn't exist
        """
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        if model_path.suffix != '.pt':
            raise ValueError("Only .pt (PyTorch) model files are supported")

        # Try to load model with ultralytics
        try:
            from ultralytics import YOLO

            logger.info(f"Loading model for validation: {model_path}")
            model = YOLO(str(model_path))

            # Extract metadata
            metadata = {
                'valid': True,
                'classes': list(model.names.values()) if hasattr(model, 'names') else [],
                'num_classes': len(model.names) if hasattr(model, 'names') else 0,
                'task': getattr(model, 'task', 'detect'),
            }

            # Try to get input size
            if hasattr(model, 'overrides'):
                metadata['imgsz'] = model.overrides.get('imgsz', 640)
            else:
                metadata['imgsz'] = 640

            logger.info(f"Model validation successful: {metadata['num_classes']} classes, task={metadata['task']}")
            return metadata

        except ImportError:
            raise ValueError("Ultralytics not installed. Install with: pip install ultralytics")
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            raise ValueError(f"Invalid model file: {str(e)}")

    def import_model(
        self,
        source_path: Path,
        name: str,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Import a model from external source.

        Args:
            source_path: Path to model file (.pt)
            name: Model name
            description: Model description
            tags: List of tags
            validate: Whether to validate model before import

        Returns:
            Dictionary with import result

        Raises:
            ValueError: If model is invalid or name exists
            FileNotFoundError: If source file doesn't exist
        """
        from ..core.registries import ModelRegistry

        # Validate name
        if not name or not name.strip():
            raise ValueError("Model name is required")

        # Check if model with this name already exists
        model_registry = ModelRegistry(self.project_root)
        existing = model_registry.get_model(name)
        if existing:
            raise ValueError(
                f"Model '{name}' already exists. "
                "Use a different name or remove the existing model."
            )

        # Validate model file
        metadata = {}
        if validate:
            logger.info("Validating model file...")
            metadata = self.validate_model_file(source_path)

        # Create model directory
        model_dir = self.models_dir / name
        model_dir.mkdir(parents=True, exist_ok=True)

        # Copy model file
        dest_path = model_dir / "model.pt"
        logger.info(f"Copying model to: {dest_path}")
        shutil.copy2(source_path, dest_path)

        # Prepare model info
        version = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        model_info = {
            'name': name,
            'version': version,
            'created': datetime.utcnow().isoformat() + 'Z',
            'run_id': None,  # Imported models don't have run_id
            'path': str(dest_path.relative_to(self.project_root)),
            'provenance': 'imported',  # Mark as imported (vs promoted)
            'metadata': {
                'description': description or '',
                'tags': tags or [],
                'source_file': str(source_path.name),
                **metadata  # Include validation metadata
            }
        }

        # Register in model registry
        logger.info(f"Registering model: {name}")
        model_registry._load_registry()  # Ensure fresh state

        import yaml
        registry_path = self.project_root / ".modelcub" / "models.yaml"

        # Load current registry
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                registry = yaml.safe_load(f) or {}
        else:
            registry = {}

        if 'models' not in registry:
            registry['models'] = {}

        # Add model
        registry['models'][name] = model_info

        # Save registry
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(registry_path, 'w') as f:
            yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Model '{name}' imported successfully")

        return model_info