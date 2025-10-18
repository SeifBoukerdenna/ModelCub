"""Project routes with proper meta."""
from typing import List
import logging
from fastapi import APIRouter
from .projects_operations import ProjectOperations
from ..dependencies import WorkingDir
from ...shared.api.config import Endpoints
from ...shared.api.schemas import (
    APIResponse, ResponseMeta,
    Project as ProjectSchema,
    ProjectConfigFull,
    CreateProjectRequest,
    SetConfigRequest,
    DeleteProjectRequest as DeleteProjectBody
)
from ...shared.api.errors import NotFoundError, ProjectError, ErrorCode, BadRequestError
from ....services.project_service import (
    init_project, delete_project,
    InitProjectRequest, DeleteProjectRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix=Endpoints.PROJECTS, tags=["Projects"])

@router.get("")
async def list_projects(working_dir: WorkingDir) -> APIResponse[List[ProjectSchema]]:
    logger.info(f"Listing projects in: {working_dir}")
    projects = ProjectOperations.list_projects(working_dir)
    return APIResponse(
        success=True,
        data=projects,
        message=f"Found {len(projects)} project(s)",
        meta=ResponseMeta()  # Always include
    )

@router.post("")
async def create_project(
    request: CreateProjectRequest,
    working_dir: WorkingDir
) -> APIResponse[ProjectSchema]:
    logger.info(f"Creating project: {request.name}")

    service_req = InitProjectRequest(
        path=str(request.path or (working_dir / request.name)),
        name=request.name,
        force=request.force
    )

    result = init_project(service_req)

    if not result.success:
        raise ProjectError(
            message=result.message,
            code=ErrorCode.PROJECT_CREATE_FAILED,
            details=result.metadata
        )

    from modelcub.sdk import Project
    project = Project.load(result.data)
    from .project_utils import project_to_schema

    return APIResponse(
        success=True,
        data=project_to_schema(project),
        message=result.message,
        meta=ResponseMeta(duration_ms=result.duration_ms)  # Include duration
    )

@router.get("/by-path")
async def get_project_by_path(path: str) -> APIResponse[ProjectSchema]:
    try:
        logger.info(f"Getting project at: {path}")
        schema = ProjectOperations.load_project(path)
        return APIResponse(
            success=True,
            data=schema,
            message=f"Project '{schema.name}' loaded successfully",
            meta=ResponseMeta()
        )
    except ValueError as e:
        raise NotFoundError(message=str(e), code=ErrorCode.PROJECT_NOT_FOUND)
    except Exception as e:
        logger.error(f"Failed to get project: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to load project: {str(e)}",
            code=ErrorCode.PROJECT_INVALID
        )

@router.delete("")
async def delete_project_route(
    body: DeleteProjectBody,
    working_dir: WorkingDir
) -> APIResponse[str]:
    logger.info(f"Deleting project: {body.path}")
    service_req = DeleteProjectRequest(target=body.path, yes=body.confirm)
    result = delete_project(service_req)

    if not result.success:
        raise ProjectError(
            message=result.message,
            code=ErrorCode.PROJECT_DELETE_FAILED,
            details=result.metadata
        )

    return APIResponse(
        success=True,
        data=result.data,
        message=result.message,
        meta=ResponseMeta(duration_ms=result.duration_ms)
    )

@router.get("/config")
async def get_project_config(path: str) -> APIResponse[ProjectConfigFull]:
    try:
        schema = ProjectOperations.get_config(path)
        return APIResponse(
            success=True,
            data=schema,
            message="Configuration loaded successfully",
            meta=ResponseMeta()
        )
    except Exception as e:
        logger.error(f"Failed to get config: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to load config: {str(e)}",
            code=ErrorCode.PROJECT_INVALID
        )

@router.post("/config")
async def set_project_config(path: str, request: SetConfigRequest) -> APIResponse[ProjectConfigFull]:
    try:
        schema = ProjectOperations.set_config(path, request)
        return APIResponse(
            success=True,
            data=schema,
            message="Configuration updated successfully",
            meta=ResponseMeta()
        )
    except Exception as e:
        logger.error(f"Failed to set config: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to update config: {str(e)}",
            code=ErrorCode.PROJECT_INVALID
        )
