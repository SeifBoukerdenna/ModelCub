"""
ModelCub SDK - Model Manager.

Provides high-level Python API for managing promoted models.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Dict, Any

from .promoted_model import PromotedModel


class ModelManager:
    """
    High-level interface for managing promoted models.

    Example:
        >>> from modelcub import Project
        >>> project = Project.load()
        >>> models = project.models
        >>> model = models.promote("run-20251027-143022", "detector-v1")
        >>> all_models = models.list()
    """

    def __init__(self, project_path: str | Path):
        """
        Initialize ModelManager.

        Args:
            project_path: Project directory path
        """
        self._project_path = Path(project_path).resolve()

    def promote(
        self,
        run_id: str,
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PromotedModel:
        """
        Promote a trained model to production.

        Takes the best weights from a training run and promotes them
        to the models registry for production use.

        Args:
            run_id: Training run ID
            name: Model name (e.g., "detector-v1", "segmenter-v2")
            description: Model description
            tags: List of tags for organization
            metadata: Additional metadata (will be merged with run metrics)

        Returns:
            PromotedModel instance

        Raises:
            ValueError: If run not found, not completed, or model name exists
            FileNotFoundError: If best weights not found

        Example:
            >>> model = models.promote("run-20251027-143022", "detector-v1")
            >>> model = models.promote(
            ...     "run-20251027-143022",
            ...     "detector-v2",
            ...     description="Improved with new data",
            ...     tags=["production", "v2"]
            ... )
        """
        from ..core.registries import RunRegistry, ModelRegistry

        run_registry = RunRegistry(self._project_path)
        model_registry = ModelRegistry(self._project_path)

        # Get run info
        run = run_registry.get_run(run_id)
        if not run:
            raise ValueError(f"Run not found: {run_id}")

        if run['status'] != 'completed':
            raise ValueError(
                f"Run must be completed (current status: {run['status']})"
            )

        # Find best weights
        run_path = self._project_path / run['artifacts_path']
        weights_dir = run_path / 'train' / 'weights'
        best_weights = weights_dir / 'best.pt'

        if not best_weights.exists():
            raise FileNotFoundError(f"Best weights not found: {best_weights}")

        # Prepare metadata
        model_metadata = metadata or {}
        model_metadata['description'] = description or ''
        model_metadata['metrics'] = run.get('metrics', {})
        model_metadata['config'] = run['config']
        model_metadata['dataset_name'] = run['dataset_name']
        model_metadata['dataset_snapshot_id'] = run['dataset_snapshot_id']

        if tags:
            model_metadata['tags'] = tags

        # Promote model
        model_registry.promote_model(
            name=name,
            run_id=run_id,
            model_path=best_weights,
            metadata=model_metadata
        )

        return PromotedModel(name, self._project_path)

    def get(self, name: str) -> PromotedModel:
        """
        Get a promoted model by name.

        Args:
            name: Model name

        Returns:
            PromotedModel instance

        Raises:
            ValueError: If model not found

        Example:
            >>> model = models.get("detector-v1")
            >>> print(model.version)
        """
        return PromotedModel(name, self._project_path)

    def list(self) -> List[PromotedModel]:
        """
        List all promoted models.

        Returns:
            List of PromotedModel instances

        Example:
            >>> models = models.list()
            >>> for model in models:
            ...     print(f"{model.name}: {model.version}")
        """
        from ..core.registries import ModelRegistry

        registry = ModelRegistry(self._project_path)
        model_dicts = registry.list_models()

        return [
            PromotedModel(model['name'], self._project_path)
            for model in model_dicts
        ]

    def remove(self, name: str, force: bool = False) -> None:
        """
        Remove a promoted model.

        Args:
            name: Model name
            force: Skip confirmation

        Example:
            >>> models.remove("detector-v1", force=True)
        """
        from ..core.registries import ModelRegistry

        if not force:
            response = input(f"Delete model '{name}'? (y/n): ")
            if response.lower() != 'y':
                print("Cancelled")
                return

        registry = ModelRegistry(self._project_path)
        registry.remove_model(name)

    def exists(self, name: str) -> bool:
        """
        Check if a model exists.

        Args:
            name: Model name

        Returns:
            True if model exists

        Example:
            >>> if models.exists("detector-v1"):
            ...     print("Model exists")
        """
        from ..core.registries import ModelRegistry

        registry = ModelRegistry(self._project_path)
        return registry.get_model(name) is not None

    def __len__(self) -> int:
        """Number of promoted models."""
        return len(self.list())

    def __iter__(self):
        """Iterate over promoted models."""
        return iter(self.list())

    def __repr__(self) -> str:
        """String representation."""
        count = len(self)
        return f"ModelManager({count} model{'s' if count != 1 else ''})"