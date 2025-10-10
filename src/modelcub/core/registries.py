"""
Dataset and Run registries.

Manages .modelcub/datasets.yaml and .modelcub/runs.yaml
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import json


class DatasetRegistry:
    """Manages .modelcub/datasets.yaml - tracks all datasets in project."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.registry_path = project_root / ".modelcub" / "datasets.yaml"
        self._data = self._load()

    def _load(self) -> dict:
        """Load registry from disk."""
        if not self.registry_path.exists():
            return {"datasets": {}}

        content = self.registry_path.read_text(encoding="utf-8")
        return self._parse_yaml(content)

    def _parse_yaml(self, content: str) -> dict:
        """Simple YAML parser for registry format."""
        # For now, use JSON as intermediate (registries can be JSON)
        # In production, you'd use a proper YAML parser
        if not content.strip():
            return {"datasets": {}}

        try:
            # Try JSON first (easier to work with)
            return json.loads(content)
        except:
            # Fallback to empty
            return {"datasets": {}}

    def save(self) -> None:
        """Save registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Use JSON for simplicity (still human-readable)
        content = json.dumps(self._data, indent=2)
        self.registry_path.write_text(content, encoding="utf-8")

    def add_dataset(self, dataset_info: dict) -> None:
        """Add or update a dataset in the registry."""
        name = dataset_info["name"]
        self._data["datasets"][name] = dataset_info
        self.save()

    def get_dataset(self, name: str) -> Optional[dict]:
        """Get dataset info by name."""
        return self._data["datasets"].get(name)

    def remove_dataset(self, name: str) -> None:
        """Remove dataset from registry."""
        if name in self._data["datasets"]:
            del self._data["datasets"][name]
            self.save()

    def list_datasets(self) -> list[dict]:
        """List all datasets."""
        return list(self._data["datasets"].values())

    def exists(self, name: str) -> bool:
        """Check if dataset exists in registry."""
        return name in self._data["datasets"]


class RunRegistry:
    """Manages .modelcub/runs.yaml - tracks all training runs."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.registry_path = project_root / ".modelcub" / "runs.yaml"
        self._data = self._load()

    def _load(self) -> dict:
        """Load registry from disk."""
        if not self.registry_path.exists():
            return {"runs": {}}

        content = self.registry_path.read_text(encoding="utf-8")
        try:
            return json.loads(content)
        except:
            return {"runs": {}}

    def save(self) -> None:
        """Save registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(self._data, indent=2)
        self.registry_path.write_text(content, encoding="utf-8")

    def add_run(self, run_info: dict) -> None:
        """Add or update a run in the registry."""
        run_id = run_info["id"]
        self._data["runs"][run_id] = run_info
        self.save()

    def get_run(self, run_id: str) -> Optional[dict]:
        """Get run info by ID."""
        return self._data["runs"].get(run_id)

    def list_runs(self) -> list[dict]:
        """List all runs."""
        return list(self._data["runs"].values())


def initialize_registries(project_root: Path) -> None:
    """Initialize empty registry files."""
    datasets_path = project_root / ".modelcub" / "datasets.yaml"
    runs_path = project_root / ".modelcub" / "runs.yaml"

    datasets_path.parent.mkdir(parents=True, exist_ok=True)

    if not datasets_path.exists():
        datasets_path.write_text('{"datasets": {}}\n', encoding="utf-8")

    if not runs_path.exists():
        runs_path.write_text('{"runs": {}}\n', encoding="utf-8")