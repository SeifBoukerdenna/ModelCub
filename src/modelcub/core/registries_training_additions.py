"""
Additional registry classes and updates for training system.

Add this code to existing src/modelcub/core/registries.py file.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from datetime import datetime


# ============================================================================
# Add these to RunRegistry class
# ============================================================================

# State transition validation (add at class level)
VALID_TRANSITIONS = {
    'pending': ['running', 'cancelled'],
    'running': ['completed', 'failed', 'cancelled'],
    'completed': [],
    'failed': [],
    'cancelled': []
}


def _validate_transition(self, current_status: str, new_status: str) -> None:
    """
    Validate state transition is allowed.

    Raises:
        ValueError: If transition is invalid
    """
    if new_status not in VALID_TRANSITIONS.get(current_status, []):
        raise ValueError(
            f"Invalid status transition: {current_status} → {new_status}"
        )


def _save_registry_atomic(self, registry: Dict) -> None:
    """
    Save registry with atomic write and file lock.

    Replace existing _save_registry() method with this.
    """
    from .io import atomic_write, FileLock

    with FileLock(self.registry_path):
        content = yaml.safe_dump(
            registry,
            default_flow_style=False,
            sort_keys=False
        )
        atomic_write(self.registry_path, content)


def update_run_validated(self, run_id: str, updates: Dict[str, Any]) -> None:
    """
    Update run information with state validation.

    Replace existing update_run() method with this.

    Args:
        run_id: Run identifier
        updates: Dictionary of fields to update

    Raises:
        ValueError: If run not found or invalid state transition
    """
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
    self._save_registry(registry)


# ============================================================================
# ModelRegistry - New class to add to registries.py
# ============================================================================

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
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        registry = self._load_registry()

        if name in registry["models"]:
            raise ValueError(f"Model '{name}' already exists. Use a different name or remove the existing model.")

        # Create model directory
        model_dir = self.models_dir / name
        model_dir.mkdir(parents=True, exist_ok=True)

        # Copy model file
        import shutil
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

        self._save_registry(registry)
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
        registry = self._load_registry()

        if name not in registry["models"]:
            raise ValueError(f"Model not found: {name}")

        # Remove model directory
        model_dir = self.models_dir / name
        if model_dir.exists():
            import shutil
            shutil.rmtree(model_dir)

        # Remove from registry
        del registry["models"][name]
        self._save_registry(registry)