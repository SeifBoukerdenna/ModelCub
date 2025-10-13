"""
ModelCub registries for datasets and training runs.
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
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
        registry = self._load_registry()
        if "datasets" not in registry:
            registry["datasets"] = {}

        dataset_id = dataset_info.get("id")
        registry["datasets"][dataset_id] = dataset_info
        self._save_registry(registry)

    def remove_dataset(self, dataset_name: str) -> None:
        """Remove dataset from registry."""
        registry = self._load_registry()
        dataset_id = None

        for ds_id, ds_info in registry.get("datasets", {}).items():
            if ds_info.get("name") == dataset_name:
                dataset_id = ds_id
                break

        if dataset_id:
            del registry["datasets"][dataset_id]
            self._save_registry(registry)

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
            class_name: Name of the class to add
            class_id: Optional specific ID for the class (auto-assigned if None)

        Returns:
            Assigned class ID

        Raises:
            DatasetNotFoundError: If dataset doesn't exist
            ClassExistsError: If class already exists
            ValueError: If class_id is already taken
        """
        if not self.exists(dataset_name):
            raise DatasetNotFoundError(f"Dataset not found: {dataset_name}")

        classes = self.list_classes(dataset_name)

        if class_name in classes:
            raise ClassExistsError(f"Class already exists: {class_name}")

        # Determine class ID
        if class_id is None:
            assigned_id = len(classes)
        else:
            if class_id < 0:
                raise ValueError("Class ID must be non-negative")
            if class_id < len(classes):
                raise ValueError(f"Class ID {class_id} already taken")
            while len(classes) < class_id:
                classes.append(None)
            assigned_id = class_id

        # Add class
        if assigned_id >= len(classes):
            classes.append(class_name)
        else:
            classes[assigned_id] = class_name

        self._update_classes(dataset_name, classes)
        return assigned_id

    def remove_class(self, dataset_name: str, class_name: str) -> None:
        """Remove a class from a dataset.

        Note: This does not delete existing labels. Use with caution.

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

        # Replace with None to preserve IDs
        class_idx = classes.index(class_name)
        classes[class_idx] = None

        # Clean trailing Nones
        while classes and classes[-1] is None:
            classes.pop()

        self._update_classes(dataset_name, classes)

    def rename_class(self, dataset_name: str, old_name: str, new_name: str) -> None:
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
        import json

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
        self._save_registry(registry)

        dataset_path = self.datasets_dir / dataset_name

        # Update/create dataset.yaml (YOLO format)
        dataset_yaml = dataset_path / "dataset.yaml"
        if dataset_yaml.exists():
            with open(dataset_yaml, 'r') as f:
                ds_config = yaml.safe_load(f) or {}
        else:
            ds_config = {"path": str(dataset_path)}  # Create new

        ds_config["names"] = clean_classes
        ds_config["nc"] = len(clean_classes)

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
        """Save runs registry to YAML."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w') as f:
            yaml.safe_dump(registry, f, default_flow_style=False, sort_keys=False)

    def list_runs(self) -> List[Dict[str, Any]]:
        """List all training runs."""
        registry = self._load_registry()
        return list(registry.get("runs", {}).values())

    def get_run(self, run_id: str) -> Dict[str, Any]:
        """Get run info by ID."""
        registry = self._load_registry()
        runs = registry.get("runs", {})
        if run_id not in runs:
            raise ValueError(f"Run not found: {run_id}")
        return runs[run_id]

    def add_run(self, run_info: Dict[str, Any]) -> None:
        """Add a new run to registry."""
        registry = self._load_registry()
        if "runs" not in registry:
            registry["runs"] = {}

        run_id = run_info.get("id")
        registry["runs"][run_id] = run_info
        self._save_registry(registry)

    def update_run(self, run_id: str, updates: Dict[str, Any]) -> None:
        """Update run information."""
        registry = self._load_registry()
        if run_id not in registry.get("runs", {}):
            raise ValueError(f"Run not found: {run_id}")

        registry["runs"][run_id].update(updates)
        self._save_registry(registry)

    def remove_run(self, run_id: str) -> None:
        """Remove run from registry."""
        registry = self._load_registry()
        if run_id in registry.get("runs", {}):
            del registry["runs"][run_id]
            self._save_registry(registry)