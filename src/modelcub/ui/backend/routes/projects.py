"""Project management API routes."""
from typing import List
import logging

from fastapi import APIRouter

from .projects_operations import ProjectOperations
from ..dependencies import WorkingDir
from ...shared.api.config import Endpoints
from ...shared.api.schemas import (
    APIResponse,
    Project as ProjectSchema,
    ProjectConfigFull,
    CreateProjectRequest,
    SetConfigRequest,
    DeleteProjectRequest as DeleteProjectBody
)
from ...shared.api.errors import NotFoundError, ProjectError, ErrorCode, BadRequestError

logger = logging.getLogger(__name__)
router = APIRouter(prefix=Endpoints.PROJECTS, tags=["Projects"])


@router.get("")
async def list_projects(working_dir: WorkingDir) -> APIResponse[List[ProjectSchema]]:
    """List all projects in working directory."""
    logger.info(f"Listing projects in: {working_dir}")
    projects = ProjectOperations.list_projects(working_dir)
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
    """Create a new project."""
    try:
        logger.info(f"Creating project: {request.name}")
        schema = ProjectOperations.create_project(
            working_dir,
            request.name,
            request.path,
            request.force
        )
        return APIResponse(
            success=True,
            data=schema,
            message=f"Project '{request.name}' created successfully"
        )
    except ValueError as e:
        raise BadRequestError(message=str(e), code=ErrorCode.PROJECT_INVALID)
    except RuntimeError as e:
        raise ProjectError(message=str(e), code=ErrorCode.PROJECT_CREATE_FAILED)
    except Exception as e:
        logger.error(f"Failed to create project: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to create project: {str(e)}",
            code=ErrorCode.PROJECT_CREATE_FAILED
        )


@router.get("/by-path")
async def get_project_by_path(path: str) -> APIResponse[ProjectSchema]:
    """Get project by path."""
    try:
        logger.info(f"Getting project at: {path}")
        schema = ProjectOperations.load_project(path)
        return APIResponse(
            success=True,
            data=schema,
            message=f"Project '{schema.name}' loaded successfully"
        )
    except ValueError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.PROJECT_NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to get project: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to load project: {str(e)}",
            code=ErrorCode.PROJECT_INVALID
        )


@router.get("/config")
async def get_project_config(path: str) -> APIResponse[ProjectConfigFull]:
    """Get project configuration."""
    try:
        logger.info(f"Getting config for project at: {path}")
        config_schema = ProjectOperations.get_config(path)
        return APIResponse(
            success=True,
            data=config_schema,
            message="Configuration loaded successfully"
        )
    except ValueError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.PROJECT_NOT_FOUND)
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

    Frontend sends a single key/value (dot-path), e.g.:
      { "key": "defaults.batch_size", "value": 32 }

    We support this shape while keeping the old explicit-field logic available
    through ProjectOperations.update_config (not removed).
    """
    try:
        logger.info(f"Updating config for project at: {path} | {request.key}={request.value!r}")
        updated = ProjectOperations.update_config_by_key(path, request.key, request.value)
        return APIResponse(
            success=True,
            data=updated,
            message="Configuration updated successfully"
        )
    except BadRequestError:
        # Raised when key is unsupported or value type is invalid
        raise
    except ValueError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.PROJECT_NOT_FOUND)
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
    """Delete a project."""
    try:
        logger.info(f"Deleting project at: {path}")
        project_name = ProjectOperations.delete_project(path, body.confirm)
        return APIResponse(
            success=True,
            data=None,
            message=f"Project '{project_name}' deleted successfully"
        )
    except ValueError as e:
        if "confirm" in str(e).lower():
            raise BadRequestError(message=str(e), code=ErrorCode.PROJECT_INVALID)
        raise NotFoundError(message=str(e), code=ErrorCode.PROJECT_NOT_FOUND)
    except RuntimeError as e:
        raise ProjectError(message=str(e), code=ErrorCode.PROJECT_DELETE_FAILED)
    except Exception as e:
        logger.error(f"Failed to delete project: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to delete project: {str(e)}",
            code=ErrorCode.PROJECT_DELETE_FAILED
        )
