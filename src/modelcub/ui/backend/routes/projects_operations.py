"""Project business logic operations."""
from typing import Optional
from pathlib import Path
import logging

from modelcub.sdk import Project

from .project_utils import project_to_schema, find_projects
from ...shared.api.schemas import (
    Project as ProjectSchema,
    ProjectConfigFull,
)

logger = logging.getLogger(__name__)


class ProjectOperations:
    """Handles project business logic operations."""

    @staticmethod
    def list_projects(working_dir: Path) -> list[ProjectSchema]:
        """List all projects in working directory."""
        return find_projects(working_dir)

    @staticmethod
    def create_project(
        working_dir: Path,
        name: str,
        path: Optional[str],
        force: bool
    ) -> ProjectSchema:
        """Create a new project."""
        # Determine project path
        if path:
            project_path = Path(path)
            if not project_path.is_absolute():
                project_path = working_dir / project_path
        else:
            project_path = working_dir / name

        # Create via SDK
        project = Project.init(name=name, path=str(project_path), force=force)
        return project_to_schema(project)

    @staticmethod
    def load_project(path: str) -> ProjectSchema:
        """Load project by path."""
        project = Project.load(path)
        return project_to_schema(project)

    @staticmethod
    def get_config(path: str) -> ProjectConfigFull:
        """Get project configuration."""
        project = Project.load(path)
        config = project.config

        return ProjectConfigFull(
            project=config.project,
            defaults=config.defaults,
            paths=config.paths
        )

    @staticmethod
    def update_config(
        path: str,
        device: Optional[str],
        batch_size: Optional[int],
        image_size: Optional[int],
        workers: Optional[int]
    ) -> ProjectConfigFull:
        """Update project configuration."""
        project = Project.load(path)

        # Update config fields
        if device is not None:
            project.config.defaults.device = device
        if batch_size is not None:
            project.config.defaults.batch_size = batch_size
        if image_size is not None:
            project.config.defaults.image_size = image_size
        if workers is not None:
            project.config.defaults.workers = workers

        # Save via SDK
        project.save_config()

        # Return updated config
        return ProjectConfigFull(
            project=project.config.project,
            defaults=project.config.defaults,
            paths=project.config.paths
        )

    @staticmethod
    def delete_project(path: str, confirm: bool) -> str:
        """Delete a project."""
        if not confirm:
            raise ValueError("Must confirm deletion")

        project = Project.load(path)
        project_name = project.name
        project.delete(confirm=True)
        return project_name