"""Project utility functions."""
from pathlib import Path
import logging

from modelcub.sdk import Project

from ...shared.api.schemas import Project as ProjectSchema, ProjectConfig

logger = logging.getLogger(__name__)


def project_to_schema(project: Project, is_current: bool = False) -> ProjectSchema:
    """Convert SDK Project to API schema."""
    return ProjectSchema(
        name=project.name,
        path=str(project.path),
        created=project.created,
        version=project.version,
        config=ProjectConfig(
            device=project.config.defaults.device,
            batch_size=project.config.defaults.batch_size,
            image_size=project.config.defaults.image_size,
            workers=project.config.defaults.workers,
            format=project.config.defaults.format
        ),
        is_current=is_current
    )


def find_projects(search_path: Path) -> list[ProjectSchema]:
    """Find all ModelCub projects in directory and subdirectories."""
    projects = []

    try:
        for item in search_path.rglob(".modelcub"):
            if item.is_dir():
                project_path = item.parent
                try:
                    project = Project.load(str(project_path))
                    projects.append(project_to_schema(project, False))
                except Exception as e:
                    logger.warning(f"Failed to load project at {project_path}: {e}")
    except Exception as e:
        logger.error(f"Failed to search for projects: {e}", exc_info=True)

    return projects