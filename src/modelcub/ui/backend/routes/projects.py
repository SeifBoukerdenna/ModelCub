"""Project management API routes - Fixed."""
from typing import List
from pathlib import Path
import logging
from dataclasses import asdict

from fastapi import APIRouter

from modelcub.services.project_service import init_project, delete_project, InitProjectRequest, DeleteProjectRequest
from modelcub.core.config import load_config, save_config
from modelcub.sdk.project import Project

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
    config = load_config(Path(project.path))
    return ProjectSchema(
        name=project.name,
        path=str(project.path),
        created=config.project.created,
        version=config.project.version,
        config=ProjectConfig(
            device=config.defaults.device,
            batch_size=config.defaults.batch_size,
            image_size=config.defaults.image_size,
            workers=config.defaults.workers,
            format=config.defaults.format
        ),
        is_current=is_current
    )


def _find_projects(search_path: Path) -> List[ProjectSchema]:
    """Find all ModelCub projects in directory and subdirectories."""
    projects = []

    try:
        for item in search_path.rglob(".modelcub"):
            if item.is_dir():
                project_path = item.parent
                try:
                    project = Project.load(str(project_path))
                    projects.append(_convert_project_to_schema(project, False))
                except Exception as e:
                    logger.warning(f"Failed to load project at {project_path}: {e}")
    except Exception as e:
        logger.error(f"Failed to search for projects: {e}", exc_info=True)

    return projects


@router.get("")
async def list_projects(working_dir: WorkingDir) -> APIResponse[List[ProjectSchema]]:
    """List all projects in working directory."""
    logger.info(f"Listing projects in: {working_dir}")
    projects = _find_projects(working_dir)
    return APIResponse(success=True, data=projects, message=f"Found {len(projects)} project(s)")


@router.post("")
async def create_project(request: CreateProjectRequest, working_dir: WorkingDir) -> APIResponse[ProjectSchema]:
    """Create a new project."""
    try:
        project_path = Path(request.path) if request.path else working_dir / request.name
        if not project_path.is_absolute():
            project_path = working_dir / project_path

        logger.info(f"Creating project '{request.name}' at: {project_path}")

        init_request = InitProjectRequest(path=str(project_path), name=request.name, force=request.force)
        code, message = init_project(init_request)

        if code != 0:
            raise ProjectError(message=message or "Failed to create project", code=ErrorCode.PROJECT_INVALID)

        project = Project.load(str(project_path))
        project_schema = _convert_project_to_schema(project, True)
        return APIResponse(success=True, data=project_schema, message=f"Project '{request.name}' created successfully")

    except ProjectError:
        raise
    except Exception as e:
        logger.error(f"Failed to create project: {e}", exc_info=True)
        raise ProjectError(message=f"Failed to create project: {str(e)}", code=ErrorCode.PROJECT_INVALID)


@router.get("/by-path")
async def get_project_by_path(path: str, working_dir: WorkingDir) -> APIResponse[ProjectSchema]:
    """Get project by path."""
    try:
        full_path = Path(path) if Path(path).is_absolute() else working_dir / path
        logger.info(f"Getting project at: {full_path}")

        if not (full_path / ".modelcub").exists():
            raise NotFoundError(message=f"Project not found at: {full_path}", code=ErrorCode.PROJECT_NOT_FOUND)

        project = Project.load(str(full_path))
        project_schema = _convert_project_to_schema(project, True)
        return APIResponse(success=True, data=project_schema, message="Project loaded successfully")

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get project: {e}", exc_info=True)
        raise ProjectError(message=f"Failed to load project: {str(e)}", code=ErrorCode.PROJECT_LOAD_FAILED)


@router.get("/config")
async def get_project_config(path: str, working_dir: WorkingDir) -> APIResponse[ProjectConfigFull]:
    """Get project configuration."""
    try:
        full_path = Path(path) if Path(path).is_absolute() else working_dir / path
        logger.info(f"Loading config from: {full_path}")

        if not (full_path / ".modelcub").exists():
            raise NotFoundError(message=f"Project not found at: {full_path}", code=ErrorCode.PROJECT_NOT_FOUND)

        config = load_config(full_path)
        if not config:
            raise NotFoundError(message=f"Configuration not found at: {full_path}", code=ErrorCode.PROJECT_NOT_FOUND)

        config_schema = ProjectConfigFull(project=asdict(config.project), defaults=asdict(config.defaults), paths=asdict(config.paths))
        return APIResponse(success=True, data=config_schema, message="Configuration loaded successfully")

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to load config: {e}", exc_info=True)
        raise ProjectError(message=f"Failed to load config: {str(e)}", code=ErrorCode.PROJECT_LOAD_FAILED)


@router.post("/config")
async def set_project_config(path: str, request: SetConfigRequest, working_dir: WorkingDir) -> APIResponse[ProjectConfigFull]:
    """Set a configuration value."""
    try:
        full_path = Path(path) if Path(path).is_absolute() else working_dir / path
        logger.info(f"Setting config for: {full_path}: {request.key} = {request.value}")

        if not (full_path / ".modelcub").exists():
            raise NotFoundError(message=f"Project not found at: {full_path}", code=ErrorCode.PROJECT_NOT_FOUND)

        if request.key.startswith("project."):
            raise BadRequestError(message="Cannot modify project metadata", code=ErrorCode.VALIDATION_ERROR)

        config = load_config(full_path)
        parts = request.key.split(".")
        if len(parts) != 2:
            raise BadRequestError(message=f"Invalid config key format: {request.key}", code=ErrorCode.VALIDATION_ERROR)

        section, key = parts
        if section == "defaults":
            if not hasattr(config.defaults, key):
                raise BadRequestError(message=f"Unknown config key: {request.key}", code=ErrorCode.VALIDATION_ERROR)
            setattr(config.defaults, key, request.value)
        elif section == "paths":
            if not hasattr(config.paths, key):
                raise BadRequestError(message=f"Unknown config key: {request.key}", code=ErrorCode.VALIDATION_ERROR)
            setattr(config.paths, key, request.value)
        else:
            raise BadRequestError(message=f"Unknown config section: {section}", code=ErrorCode.VALIDATION_ERROR)

        save_config(full_path, config)
        config_schema = ProjectConfigFull(project=asdict(config.project), defaults=asdict(config.defaults), paths=asdict(config.paths))
        return APIResponse(success=True, data=config_schema, message=f"Configuration updated: {request.key} = {request.value}")

    except (NotFoundError, BadRequestError):
        raise
    except Exception as e:
        logger.error(f"Failed to update config: {e}", exc_info=True)
        raise ProjectError(message=f"Failed to update config: {str(e)}", code=ErrorCode.PROJECT_INVALID)


@router.delete("/delete")
async def delete_project_endpoint(path: str, request: DeleteProjectBody, working_dir: WorkingDir) -> APIResponse[None]:
    """Delete a project."""
    try:
        full_path = Path(path) if Path(path).is_absolute() else working_dir / path
        logger.info(f"Deleting project at: {full_path}")

        if not request.confirm:
            raise BadRequestError(message="Deletion not confirmed", code=ErrorCode.VALIDATION_ERROR)

        if not (full_path / ".modelcub").exists():
            raise NotFoundError(message=f"Project not found at: {full_path}", code=ErrorCode.PROJECT_NOT_FOUND)

        delete_request = DeleteProjectRequest(target=str(full_path), yes=True)
        code, message = delete_project(delete_request)

        if code != 0:
            raise ProjectError(message=message or "Failed to delete project", code=ErrorCode.PROJECT_INVALID)

        return APIResponse(success=True, data=None, message=f"Project deleted: {full_path}")

    except (NotFoundError, BadRequestError, ProjectError):
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {e}", exc_info=True)
        raise ProjectError(message=f"Failed to delete project: {str(e)}", code=ErrorCode.PROJECT_INVALID)