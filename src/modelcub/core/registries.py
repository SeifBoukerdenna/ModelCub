"""
ModelCub registries for datasets, training runs, and models.
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
import json
from datetime import datetime

from modelcub.core.exceptions import (
    DatasetNotFoundError,
    ClassExistsError,
    ClassNotFoundError
)


def initialize_registries(project_root: Path) -> None:
    """Initialize empty registry files for a new project.

    Args:
        project_root: Path to the project root directory
    """
    modelcub_dir = project_root / ".modelcub"
    modelcub_dir.mkdir(parents=True, exist_ok=True)

    # Initialize datasets.yaml
    datasets_yaml = modelcub_dir / "datasets.yaml"
    if not datasets_yaml.exists():
        with open(datasets_yaml, 'w') as f:
            yaml.safe_dump({"datasets": {}}, f)

    # Initialize runs.yaml
    runs_yaml = modelcub_dir / "runs.yaml"
    if not runs_yaml.exists():
        with open(runs_yaml, 'w') as f:
            yaml.safe_dump({"runs": {}}, f)

    # Initialize models.yaml
    models_yaml = modelcub_dir / "models.yaml"
    if not models_yaml.exists():
        with open(models_yaml, 'w') as f:
            yaml.safe_dump({"models": {}}, f)

    # Initialize inferences.yaml
    inferences_yaml = modelcub_dir / "inferences.yaml"
    if not inferences_yaml.exists():
        with open(inferences_yaml, 'w') as f:
            yaml.safe_dump({"inferences": {}}, f)


class DatasetRegistry:
    """Registry for managing datasets."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.registry_path = self.project_root / ".modelcub" / "datasets.yaml"
        self.datasets_dir = self.project_root / "data" / "datasets"

    def _load_registry(self) -> Dict:
        """Load datasets registry from YAML."""
        if not self.registry_path.exists():
            return {"datasets": {}}
        with open(self.registry_path, 'r') as f:
            return yaml.safe_load(f) or {"datasets": {}}

    def _save_registry(self, registry: Dict) -> None:
        """Save datasets registry to YAML."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w') as f:
            yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)

    def save(self) -> None:
        """Save the current registry state (for compatibility)."""
        # Load current state and save it back
        registry = self._load_registry()
        self._save_registry(registry)

    def exists(self, dataset_name: str) -> bool:
        """Check if dataset exists."""
        registry = self._load_registry()
        for ds_info in registry.get("datasets", {}).values():
            if ds_info.get("name") == dataset_name:
                return True
        return False

    def get_images(
        self,
        dataset_name: str,
        split: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Dict], int]:
        """Get list of all images in the dataset."""
        dataset_path = self.datasets_dir / dataset_name

        # Determine directories to scan
        if split:
            image_dirs = [dataset_path / "images" / split]
        else:
            image_dirs = [
                dataset_path / "images" / s
                for s in ["train", "val", "test", "unlabeled"]
            ]

        # Collect image files
        images = []
        for img_dir in image_dirs:
            if not img_dir.exists():
                continue

            split_name = img_dir.name
            for img_file in img_dir.glob("*.*"):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                    label_dir = dataset_path / "labels" / split_name
                    label_file = label_dir / f"{img_file.stem}.txt"

                    images.append({
                        'name': img_file.name,
                        'path': str(img_file.relative_to(dataset_path)),
                        'split': split_name,
                        'size': img_file.stat().st_size,
                        'has_label': label_file.exists()
                    })

        total = len(images)
        images = images[offset:offset + limit]
        return images, total

    def get_dataset(self, dataset_name: str) -> Dict[str, Any]:
        """Get dataset info by name."""
        registry = self._load_registry()
        for ds_info in registry.get("datasets", {}).values():
            if ds_info.get("name") == dataset_name:
                return ds_info
        raise DatasetNotFoundError(f"Dataset not found: {dataset_name}")

    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets."""
        registry = self._load_registry()
        return list(registry.get("datasets", {}).values())

    def add_dataset(self, dataset_info: Dict[str, Any]) -> None:
        """Add a new dataset to registry."""
        from .io import FileLock

        with FileLock(self.registry_path):
            registry = self._load_registry()
            if "datasets" not in registry:
                registry["datasets"] = {}

            dataset_id = dataset_info.get("id")
            registry["datasets"][dataset_id] = dataset_info

            # Save without additional lock
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'w') as f:
                yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)

    def remove_dataset(self, dataset_name: str) -> None:
        """Remove dataset from registry."""
        from .io import FileLock

        with FileLock(self.registry_path):
            registry = self._load_registry()
            dataset_id = None

            for ds_id, ds_info in registry.get("datasets", {}).items():
                if ds_info.get("name") == dataset_name:
                    dataset_id = ds_id
                    break

            if dataset_id:
                del registry["datasets"][dataset_id]

                # Save without additional lock
                self.registry_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.registry_path, 'w') as f:
                    yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)

    def list_images(
        self,
        dataset_name: str,
        split: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Dict], int]:
        """List images in a dataset with pagination."""
        if not self.exists(dataset_name):
            raise DatasetNotFoundError(f"Dataset not found: {dataset_name}")

        return self.get_images(dataset_name, split, limit, offset)

    # ========================================================================
    # CLASS MANAGEMENT METHODS
    # ========================================================================

    def list_classes(self, dataset_name: str) -> List[str]:
        """List all classes in a dataset.

        Args:
            dataset_name: Name of the dataset

        Returns:
            List of class names in order

        Raises:
            DatasetNotFoundError: If dataset doesn't exist
        """
        if not self.exists(dataset_name):
            raise DatasetNotFoundError(f"Dataset not found: {dataset_name}")

        dataset_info = self.get_dataset(dataset_name)
        return dataset_info.get("classes", [])

    def add_class(
        self,
        dataset_name: str,
        class_name: str,
        class_id: Optional[int] = None
    ) -> int:
        """Add a new class to a dataset.

        Args:
            dataset_name: Name of the dataset
            class_name: Name of the new class
            class_id: Optional class ID (appends to end if not provided)

        Returns:
            The class ID of the added class

        Raises:
            DatasetNotFoundError: If dataset doesn't exist
            ClassExistsError: If class already exists
        """
        if not self.exists(dataset_name):
            raise DatasetNotFoundError(f"Dataset not found: {dataset_name}")

        classes = self.list_classes(dataset_name)

        if class_name in classes:
            raise ClassExistsError(f"Class already exists: {class_name}")

        if class_id is None:
            class_id = len(classes)
            classes.append(class_name)
        else:
            # Insert at specific position, fill with None if needed
            while len(classes) <= class_id:
                classes.append(None)
            classes[class_id] = class_name

        self._update_classes(dataset_name, classes)
        return class_id

    def remove_class(self, dataset_name: str, class_name: str) -> None:
        """Remove a class from a dataset.

        Args:
            dataset_name: Name of the dataset
            class_name: Name of the class to remove

        Raises:
            DatasetNotFoundError: If dataset doesn't exist
            ClassNotFoundError: If class doesn't exist
        """
        if not self.exists(dataset_name):
            raise DatasetNotFoundError(f"Dataset not found: {dataset_name}")

        classes = self.list_classes(dataset_name)

        if class_name not in classes:
            raise ClassNotFoundError(f"Class not found: {class_name}")

        class_idx = classes.index(class_name)
        classes[class_idx] = None

        self._update_classes(dataset_name, classes)

    def rename_class(
        self,
        dataset_name: str,
        old_name: str,
        new_name: str
    ) -> None:
        """Rename a class in a dataset.

        Args:
            dataset_name: Name of the dataset
            old_name: Current class name
            new_name: New class name

        Raises:
            DatasetNotFoundError: If dataset doesn't exist
            ClassNotFoundError: If old class doesn't exist
            ClassExistsError: If new class name already exists
        """
        if not self.exists(dataset_name):
            raise DatasetNotFoundError(f"Dataset not found: {dataset_name}")

        classes = self.list_classes(dataset_name)

        if old_name not in classes:
            raise ClassNotFoundError(f"Class not found: {old_name}")

        if new_name in classes:
            raise ClassExistsError(f"Class already exists: {new_name}")

        class_idx = classes.index(old_name)
        classes[class_idx] = new_name

        self._update_classes(dataset_name, classes)

    def _update_classes(self, dataset_name: str, classes: List[Optional[str]]) -> None:
        """Update classes in registry, dataset.yaml, and manifest.json."""
        from .io import FileLock

        with FileLock(self.registry_path):
            registry = self._load_registry()

            # Find dataset ID
            dataset_id = None
            for ds_id, ds_info in registry.get("datasets", {}).items():
                if ds_info.get("name") == dataset_name:
                    dataset_id = ds_id
                    break

            if not dataset_id:
                raise DatasetNotFoundError(f"Dataset not found: {dataset_name}")

            # Filter out None values
            clean_classes = [c for c in classes if c is not None]

            # Update registry
            registry["datasets"][dataset_id]["classes"] = clean_classes
            registry["datasets"][dataset_id]["num_classes"] = len(clean_classes)

            # Save without additional lock
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'w') as f:
                yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)

        # Update dataset files (outside the lock)
        dataset_path = self.datasets_dir / dataset_name

        # Update/create dataset.yaml (YOLO format)
        dataset_yaml = dataset_path / "dataset.yaml"
        if dataset_yaml.exists():
            with open(dataset_yaml, 'r') as f:
                ds_config = yaml.safe_load(f) or {}
        else:
            ds_config = {
                "path": str(dataset_path),
                "train": "train/images",
                "val": "val/images",
                "test": "test/images"
            }

        ds_config["names"] = clean_classes
        ds_config["nc"] = len(clean_classes)

        if "train" not in ds_config:
            ds_config["train"] = "train/images"
        if "val" not in ds_config:
            ds_config["val"] = "val/images"
        if "test" not in ds_config:
            ds_config["test"] = "test/images"

        with open(dataset_yaml, 'w') as f:
            yaml.safe_dump(ds_config, f, default_flow_style=False, sort_keys=False)

        # Update manifest.json (SDK format)
        manifest_json = dataset_path / "manifest.json"
        if manifest_json.exists():
            with open(manifest_json, 'r') as f:
                manifest = json.load(f)

            manifest["classes"] = clean_classes

            with open(manifest_json, 'w') as f:
                json.dump(manifest, f, indent=2)


class RunRegistry:
    """Registry for managing training runs."""

    # State transition validation
    VALID_TRANSITIONS = {
        'pending': ['running', 'cancelled', 'failed'],
        'running': ['completed', 'failed', 'cancelled'],
        'completed': [],
        'failed': [],
        'cancelled': []
    }

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.registry_path = self.project_root / ".modelcub" / "runs.yaml"

    def _load_registry(self) -> Dict:
        """Load runs registry from YAML."""
        if not self.registry_path.exists():
            return {"runs": {}}
        with open(self.registry_path, 'r') as f:
            return yaml.safe_load(f) or {"runs": {}}

    def _save_registry(self, registry: Dict) -> None:
        """Save registry with atomic write and file lock."""
        from .io import atomic_write, FileLock

        with FileLock(self.registry_path):
            content = yaml.safe_dump(
                registry,
                default_flow_style=False,
                sort_keys=False
            )
            atomic_write(self.registry_path, content)

    def _validate_transition(self, current_status: str, new_status: str) -> None:
        """
        Validate state transition is allowed.

        Raises:
            ValueError: If transition is invalid
        """
        if new_status not in self.VALID_TRANSITIONS.get(current_status, []):
            raise ValueError(
                f"Invalid status transition: {current_status} → {new_status}"
            )

    def list_runs(self) -> List[Dict[str, Any]]:
        """List all training runs."""
        registry = self._load_registry()
        return list(registry.get("runs", {}).values())

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run info by ID."""
        registry = self._load_registry()
        return registry.get("runs", {}).get(run_id)

    def add_run(self, run_info: Dict[str, Any]) -> None:
        """Add a new run to registry."""
        from .io import FileLock

        with FileLock(self.registry_path):
            registry = self._load_registry()
            if "runs" not in registry:
                registry["runs"] = {}

            run_id = run_info.get("id")
            registry["runs"][run_id] = run_info

            # Save without additional lock (we already hold it)
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'w') as f:
                yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)

    def update_run(self, run_id: str, updates: Dict[str, Any]) -> None:
        """
        Update run information with state validation.

        Args:
            run_id: Run identifier
            updates: Dictionary of fields to update

        Raises:
            ValueError: If run not found or invalid state transition
        """
        from .io import FileLock

        with FileLock(self.registry_path):
            registry = self._load_registry()
            if run_id not in registry.get("runs", {}):
                raise ValueError(f"Run not found: {run_id}")

            # Validate state transitions
            if "status" in updates:
                current_status = registry["runs"][run_id].get("status")
                new_status = updates["status"]
                if current_status:
                    self._validate_transition(current_status, new_status)

            registry["runs"][run_id].update(updates)

            # Save without additional lock
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'w') as f:
                yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)

    def remove_run(self, run_id: str) -> None:
        """Remove run from registry."""
        from .io import FileLock

        with FileLock(self.registry_path):
            registry = self._load_registry()
            if run_id in registry.get("runs", {}):
                del registry["runs"][run_id]

                # Save without additional lock
                self.registry_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.registry_path, 'w') as f:
                    yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)


class ModelRegistry:
    """
    Registry for managing promoted models.

    Tracks models that have been promoted from training runs
    for production use.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.registry_path = self.project_root / ".modelcub" / "models.yaml"
        self.models_dir = self.project_root / "models"

    def _load_registry(self) -> Dict:
        """Load models registry from YAML."""
        if not self.registry_path.exists():
            return {"models": {}}

        with open(self.registry_path, 'r') as f:
            return yaml.safe_load(f) or {"models": {}}

    def _save_registry(self, registry: Dict) -> None:
        """Save registry with atomic write and file lock."""
        from .io import atomic_write, FileLock

        with FileLock(self.registry_path):
            content = yaml.safe_dump(
                registry,
                default_flow_style=False,
                sort_keys=False
            )
            atomic_write(self.registry_path, content)

    def promote_model(
        self,
        name: str,
        run_id: str,
        model_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Promote a trained model to production.

        Args:
            name: Model name (e.g., "detector-v1")
            run_id: Training run that produced this model
            model_path: Path to model weights (e.g., best.pt)
            metadata: Optional metadata (metrics, description, etc.)

        Returns:
            Version identifier for the promoted model

        Raises:
            FileNotFoundError: If model_path doesn't exist
            ValueError: If model already exists with this name
        """
        from .io import FileLock
        import shutil

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        with FileLock(self.registry_path):
            registry = self._load_registry()

            if name in registry["models"]:
                raise ValueError(
                    f"Model '{name}' already exists. "
                    "Use a different name or remove the existing model."
                )

            # Create model directory
            model_dir = self.models_dir / name
            model_dir.mkdir(parents=True, exist_ok=True)

            # Copy model file
            dest_path = model_dir / model_path.name
            shutil.copy2(model_path, dest_path)

            # Create registry entry
            version = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
            registry["models"][name] = {
                'name': name,
                'version': version,
                'created': datetime.utcnow().isoformat() + 'Z',
                'run_id': run_id,
                'path': str(dest_path.relative_to(self.project_root)),
                'metadata': metadata or {}
            }

            # Save without additional lock
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'w') as f:
                yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)

        return version

    def get_model(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get model information by name.

        Args:
            name: Model name

        Returns:
            Model dictionary or None if not found
        """
        registry = self._load_registry()
        return registry["models"].get(name)

    def list_models(self) -> list[Dict[str, Any]]:
        """
        List all promoted models.

        Returns:
            List of model dictionaries
        """
        registry = self._load_registry()
        return list(registry["models"].values())

    def remove_model(self, name: str) -> None:
        """
        Remove a promoted model.

        Args:
            name: Model name

        Raises:
            ValueError: If model not found
        """
        from .io import FileLock
        import shutil

        with FileLock(self.registry_path):
            registry = self._load_registry()

            if name not in registry["models"]:
                raise ValueError(f"Model not found: {name}")

            # Remove model directory
            model_dir = self.models_dir / name
            if model_dir.exists():
                shutil.rmtree(model_dir)

            # Remove from registry
            del registry["models"][name]

            # Save without additional lock
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'w') as f:
                yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)


class InferenceRegistry:
    """Registry for managing inference jobs."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.registry_path = self.project_root / ".modelcub" / "inferences.yaml"

    def _load_registry(self) -> Dict:
        """Load inferences registry from YAML."""
        if not self.registry_path.exists():
            return {"inferences": {}}

        with open(self.registry_path, 'r') as f:
            return yaml.safe_load(f) or {"inferences": {}}

    def _save_registry(self, registry: Dict) -> None:
        """Save registry with atomic write and file lock."""
        from .io import atomic_write, FileLock

        with FileLock(self.registry_path):
            content = yaml.safe_dump(
                registry,
                default_flow_style=False,
                sort_keys=False
            )
            atomic_write(self.registry_path, content)

    def add_inference(self, inference_info: Dict[str, Any]) -> None:
        """Add inference job to registry."""
        registry = self._load_registry()

        inference_id = inference_info['id']
        registry['inferences'][inference_id] = inference_info

        self._save_registry(registry)

    def update_inference(self, inference_id: str, updates: Dict[str, Any]) -> None:
        """Update inference job information."""
        from .io import FileLock

        with FileLock(self.registry_path):
            registry = self._load_registry()

            if inference_id not in registry.get("inferences", {}):
                raise ValueError(f"Inference job not found: {inference_id}")

            registry["inferences"][inference_id].update(updates)

            # Save without additional lock
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, 'w') as f:
                yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)

    def get_inference(self, inference_id: str) -> Optional[Dict]:
        """Get inference job by ID."""
        registry = self._load_registry()
        return registry.get("inferences", {}).get(inference_id)

    def list_inferences(self) -> List[Dict]:
        """List all inference jobs."""
        registry = self._load_registry()
        return list(registry.get("inferences", {}).values())


    def remove_inference(self, inference_id: str) -> None:
        """Remove inference from registry."""
        from .io import FileLock

        with FileLock(self.registry_path):
            registry = self._load_registry()
            if inference_id in registry.get("inferences", {}):
                del registry["inferences"][inference_id]

                # Save without additional lock
                self.registry_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.registry_path, 'w') as f:
                    yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)