"""Base service class with common functionality."""
from typing import Optional
from pathlib import Path
import logging

from modelcub.core.config import load_config, Config
from modelcub.core.exceptions import ProjectNotFoundError


class BaseService:
    """Base service with common functionality for all services."""

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize service.

        Args:
            project_path: Path to project. If None, uses current directory.
        """
        self.project_path = project_path or Path.cwd()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._config: Optional[Config] = None

    @property
    def config(self) -> Config:
        """Get project configuration.

        Returns:
            Project configuration

        Raises:
            ProjectNotFoundError: If no project found
        """
        if self._config is None:
            self._config = load_config(self.project_path)
            if self._config is None:
                raise ProjectNotFoundError(
                    f"No ModelCub project found at {self.project_path}"
                )
        return self._config

    def reload_config(self) -> None:
        """Reload configuration from disk."""
        self._config = None

    def get_project_root(self) -> Path:
        """Get project root directory."""
        return self.project_path

    def get_data_dir(self) -> Path:
        """Get data directory."""
        return self.project_path / self.config.paths.data

    def get_runs_dir(self) -> Path:
        """Get runs directory."""
        return self.project_path / self.config.paths.runs

    def get_reports_dir(self) -> Path:
        """Get reports directory."""
        return self.project_path / self.config.paths.reports