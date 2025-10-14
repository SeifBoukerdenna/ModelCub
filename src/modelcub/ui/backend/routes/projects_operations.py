"""Project business logic operations."""
from typing import Optional
from pathlib import Path
import logging

from modelcub.sdk import Project

from .project_utils import project_to_schema, find_projects
from ...shared.api.schemas import (
    Project as ProjectSchema,
    ProjectConfigFull,
    ProjectInfo,
    ProjectPaths,
    ProjectConfig as ProjectDefaultsSchema,
)
from ...shared.api.errors import BadRequestError, ErrorCode

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

    # ------------------ internal helper: dataclass -> pydantic ------------------

    @staticmethod
    def _to_config_full_pydantic(cfg) -> ProjectConfigFull:
        """
        Convert SDK dataclass config to pydantic ProjectConfigFull.
        cfg has dataclass sections: cfg.project, cfg.defaults, cfg.paths
        """
        project_info = ProjectInfo(
            name=cfg.project.name,
            created=cfg.project.created,
            version=cfg.project.version,
        )
        defaults = ProjectDefaultsSchema(
            device=cfg.defaults.device,
            batch_size=cfg.defaults.batch_size,
            image_size=cfg.defaults.image_size,
            workers=cfg.defaults.workers,
            format=cfg.defaults.format,
        )
        paths = ProjectPaths(
            data=cfg.paths.data,
            runs=cfg.paths.runs,
            reports=cfg.paths.reports,
        )
        return ProjectConfigFull(project=project_info, defaults=defaults, paths=paths)

    # ---------------------------------------------------------------------------

    @staticmethod
    def get_config(path: str) -> ProjectConfigFull:
        """Get project configuration."""
        project = Project.load(path)
        config = project.config
        a = self_or_none = ProjectOperations._to_config_full_pydantic(config)
        # Return pydantic-safe object
        return ProjectOperations._to_config_full_pydantic(config)

    @staticmethod
    def update_config(
        path: str,
        device: Optional[str],
        batch_size: Optional[int],
        image_size: Optional[int],
        workers: Optional[int]
    ) -> ProjectConfigFull:
        """Update project configuration (explicit field mode)."""
        project = Project.load(path)

        # Update config fields
        if device is not None:
            project.config.defaults.device = device
        if batch_size is not None:
            project.config.defaults.batch_size = int(batch_size)
        if image_size is not None:
            project.config.defaults.image_size = int(image_size)
        if workers is not None:
            project.config.defaults.workers = int(workers)

        # Save via SDK
        project.save_config()

        # Return updated config (pydantic)
        return ProjectOperations._to_config_full_pydantic(project.config)

    @staticmethod
    def update_config_by_key(path: str, key: str, value) -> ProjectConfigFull:
        """
        Update project configuration using a single dot-path key/value.
        Supported keys:
          - defaults.device
          - defaults.batch_size
          - defaults.image_size
          - defaults.workers
        """
        project = Project.load(path)

        allowed = {
            "defaults.device": ("defaults", "device", str),
            "defaults.batch_size": ("defaults", "batch_size", int),
            "defaults.image_size": ("defaults", "image_size", int),
            "defaults.workers": ("defaults", "workers", int),
        }

        if key not in allowed:
            raise BadRequestError(
                message=f"Unsupported config key: {key}",
                code=ErrorCode.PROJECT_INVALID,
            )

        section, attr, caster = allowed[key]
        section_obj = getattr(project.config, section)

        try:
            cast_value = caster(value)
        except Exception:
            raise BadRequestError(
                message=f"Invalid value type for {key}: {value!r}",
                code=ErrorCode.PROJECT_INVALID,
            )

        setattr(section_obj, attr, cast_value)

        project.save_config()

        return ProjectOperations._to_config_full_pydantic(project.config)

    @staticmethod
    def delete_project(path: str, confirm: bool) -> str:
        """Delete a project."""
        if not confirm:
            raise ValueError("Must confirm deletion")

        project = Project.load(path)
        project_name = project.name
        project.delete(confirm=True)
        return project_name
