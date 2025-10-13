"""
Project management API routes - SDK-only implementation.

All operations go through the SDK as the single source of truth.
"""
from typing import List
from pathlib import Path
import logging

from fastapi import APIRouter

from modelcub.sdk import Project

from ..dependencies import WorkingDir
from ...shared.api.config import Endpoints
from ...shared.api.schemas import (
    APIResponse,
    Project as ProjectSchema,
    ProjectConfig,
    ProjectConfigFull,
    CreateProjectRequest,
    SetConfigRequest,
    DeleteProjectRequest as DeleteProjectBody
)
from ...shared.api.errors import NotFoundError, ProjectError, ErrorCode, BadRequestError

logger = logging.getLogger(__name__)
router = APIRouter(prefix=Endpoints.PROJECTS, tags=["Projects"])


def _convert_project_to_schema(project: Project, is_current: bool = False) -> ProjectSchema:
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


def _find_projects(search_path: Path) -> List[ProjectSchema]:
    """Find all ModelCub projects in directory and subdirectories using SDK."""
    projects = []

    try:
        for item in search_path.rglob(".modelcub"):
            if item.is_dir():
                project_path = item.parent
                try:
                    # Use SDK to load project
                    project = Project.load(str(project_path))
                    projects.append(_convert_project_to_schema(project, False))
                except Exception as e:
                    logger.warning(f"Failed to load project at {project_path}: {e}")
    except Exception as e:
        logger.error(f"Failed to search for projects: {e}", exc_info=True)

    return projects


@router.get("")
async def list_projects(working_dir: WorkingDir) -> APIResponse[List[ProjectSchema]]:
    """
    List all projects in working directory.

    Uses SDK: Project.load() for each discovered project.
    """
    logger.info(f"Listing projects in: {working_dir}")
    projects = _find_projects(working_dir)
    return APIResponse(
        success=True,
        data=projects,
        message=f"Found {len(projects)} project(s)"
    )


@router.post("")
async def create_project(
    request: CreateProjectRequest,
    working_dir: WorkingDir
) -> APIResponse[ProjectSchema]:
    """
    Create a new project.

    Uses SDK: Project.init()
    """
    try:
        logger.info(f"Creating project: {request.name}")

        # Determine project path
        if request.path:
            project_path = Path(request.path)
            if not project_path.is_absolute():
                project_path = working_dir / project_path
        else:
            project_path = working_dir / request.name

        # Use SDK to create project
        project = Project.init(
            name=request.name,
            path=str(project_path),
            force=request.force
        )

        schema = _convert_project_to_schema(project)

        return APIResponse(
            success=True,
            data=schema,
            message=f"Project '{request.name}' created successfully"
        )

    except ValueError as e:
        raise BadRequestError(
            message=str(e),
            code=ErrorCode.PROJECT_INVALID
        )
    except RuntimeError as e:
        raise ProjectError(
            message=str(e),
            code=ErrorCode.PROJECT_CREATE_FAILED
        )
    except Exception as e:
        logger.error(f"Failed to create project: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to create project: {str(e)}",
            code=ErrorCode.PROJECT_CREATE_FAILED
        )


@router.get("/by-path")
async def get_project_by_path(path: str) -> APIResponse[ProjectSchema]:
    """
    Get project by path.

    Uses SDK: Project.load()
    """
    try:
        logger.info(f"Getting project at: {path}")

        # Use SDK to load project
        project = Project.load(path)
        schema = _convert_project_to_schema(project)

        return APIResponse(
            success=True,
            data=schema,
            message=f"Project '{project.name}' loaded successfully"
        )

    except ValueError as e:
        raise NotFoundError(
            message=str(e),
            code=ErrorCode.PROJECT_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to get project: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to load project: {str(e)}",
            code=ErrorCode.PROJECT_INVALID
        )


@router.get("/config")
async def get_project_config(path: str) -> APIResponse[ProjectConfigFull]:
    """
    Get project configuration.

    Uses SDK: Project.load() and project.config
    """
    try:
        logger.info(f"Getting config for project at: {path}")

        # Use SDK to load project
        project = Project.load(path)
        config = project.config

        config_schema = ProjectConfigFull(
            project=config.project,
            defaults=config.defaults,
            paths=config.paths
        )

        return APIResponse(
            success=True,
            data=config_schema,
            message="Configuration loaded successfully"
        )

    except ValueError as e:
        raise NotFoundError(
            message=str(e),
            code=ErrorCode.PROJECT_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to get config: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to load configuration: {str(e)}",
            code=ErrorCode.PROJECT_INVALID
        )


@router.post("/config")
async def set_project_config(
    path: str,
    request: SetConfigRequest
) -> APIResponse[ProjectConfigFull]:
    """
    Update project configuration.

    Uses SDK: Project.load(), project.config, project.save_config()
    """
    try:
        logger.info(f"Updating config for project at: {path}")

        # Use SDK to load project
        project = Project.load(path)

        # Update configuration
        if request.device is not None:
            project.config.defaults.device = request.device
        if request.batch_size is not None:
            project.config.defaults.batch_size = request.batch_size
        if request.image_size is not None:
            project.config.defaults.image_size = request.image_size
        if request.workers is not None:
            project.config.defaults.workers = request.workers

        # Save using SDK
        project.save_config()

        # Return updated config
        config_schema = ProjectConfigFull(
            project=project.config.project,
            defaults=project.config.defaults,
            paths=project.config.paths
        )

        return APIResponse(
            success=True,
            data=config_schema,
            message="Configuration updated successfully"
        )

    except ValueError as e:
        raise NotFoundError(
            message=str(e),
            code=ErrorCode.PROJECT_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to update config: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to update configuration: {str(e)}",
            code=ErrorCode.PROJECT_INVALID
        )


@router.delete("/delete")
async def delete_project(
    path: str,
    body: DeleteProjectBody
) -> APIResponse[None]:
    """
    Delete a project.

    Uses SDK: Project.load() and project.delete()
    """
    try:
        logger.info(f"Deleting project at: {path}")

        if not body.confirm:
            raise BadRequestError(
                message="Must confirm deletion",
                code=ErrorCode.PROJECT_INVALID
            )

        # Use SDK to load and delete project
        project = Project.load(path)
        project_name = project.name

        project.delete(confirm=True)

        return APIResponse(
            success=True,
            data=None,
            message=f"Project '{project_name}' deleted successfully"
        )

    except ValueError as e:
        raise NotFoundError(
            message=str(e),
            code=ErrorCode.PROJECT_NOT_FOUND
        )
    except RuntimeError as e:
        raise ProjectError(
            message=str(e),
            code=ErrorCode.PROJECT_DELETE_FAILED
        )
    except Exception as e:
        logger.error(f"Failed to delete project: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to delete project: {str(e)}",
            code=ErrorCode.PROJECT_DELETE_FAILED
        )