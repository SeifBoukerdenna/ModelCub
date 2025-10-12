"""Project management API routes."""
from typing import Optional, List
from pathlib import Path
import os
import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

# Import from core services (outside ui/)
from modelcub.services.project_service import (
    init_project,
    delete_project,
    InitProjectRequest,
    DeleteProjectRequest
)
from modelcub.core.config import load_config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/projects")


# Request/Response models
class CreateProjectRequest(BaseModel):
    """Request model for creating a project."""
    name: str = Field(..., min_length=1, max_length=100)
    path: Optional[str] = None
    force: bool = False

class SetConfigRequest(BaseModel):
    """Request model for setting config."""
    key: str
    value: str | int | bool | float



class DeleteProjectBody(BaseModel):
    """Request body for deleting a project."""
    confirm: bool = False


class ProjectConfig(BaseModel):
    """Project configuration."""
    device: str
    batch_size: int
    image_size: int
    format: str


class ProjectResponse(BaseModel):
    """Project response model."""
    name: str
    path: str
    created: str
    version: str
    config: ProjectConfig
    is_current: bool = False


class ApiResponse(BaseModel):
    """Standard API response."""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


# Get the working directory where the UI was launched
WORKING_DIR = Path(os.environ.get("MODELCUB_WORKING_DIR", Path.cwd()))
logger.info(f"🔍 API Working directory: {WORKING_DIR}")


# Helper function to find all projects
def find_projects(search_path: Path = None) -> List[ProjectResponse]:
    """Find all ModelCub projects in current directory and subdirectories."""
    if search_path is None:
        search_path = WORKING_DIR

    logger.info(f"🔍 Searching for projects in: {search_path}")
    projects = []
    current_path = WORKING_DIR

    # Check current directory
    if (search_path / ".modelcub").exists():
        config = load_config(search_path)
        if config:
            projects.append(ProjectResponse(
                name=config.project.name,
                path=str(search_path),
                created=config.project.created,
                version=config.project.version,
                config=ProjectConfig(
                    device=config.defaults.device,
                    batch_size=config.defaults.batch_size,
                    image_size=config.defaults.image_size,
                    format=config.defaults.format,
                ),
                is_current=search_path.resolve() == current_path.resolve()
            ))

    # Check subdirectories (one level deep)
    try:
        for item in search_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if (item / ".modelcub").exists():
                    config = load_config(item)
                    if config:
                        projects.append(ProjectResponse(
                            name=config.project.name,
                            path=str(item),
                            created=config.project.created,
                            version=config.project.version,
                            config=ProjectConfig(
                                device=config.defaults.device,
                                batch_size=config.defaults.batch_size,
                                image_size=config.defaults.image_size,
                                format=config.defaults.format,
                            ),
                            is_current=item.resolve() == current_path.resolve()
                        ))
    except PermissionError:
        pass

    logger.info(f"✅ Found {len(projects)} projects")
    return projects


# Routes
@router.get("/")
async def list_projects():
    """List all ModelCub projects in current directory."""
    try:
        projects = find_projects()
        return {
            "success": True,
            "projects": [p.model_dump() for p in projects],
            "count": len(projects),
            "working_dir": str(WORKING_DIR)
        }
    except Exception as e:
        logger.error(f"❌ Failed to list projects: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )


@router.get("/current")
async def get_current_project():
    """Get current project information."""
    try:
        logger.info(f"🔍 Loading current project from: {WORKING_DIR}")
        config = load_config(WORKING_DIR)

        if not config:
            return {
                "exists": False,
                "project": None
            }

        return {
            "exists": True,
            "project": {
                "name": config.project.name,
                "created": config.project.created,
                "version": config.project.version,
                "path": str(WORKING_DIR),
                "config": {
                    "device": config.defaults.device,
                    "batch_size": config.defaults.batch_size,
                    "image_size": config.defaults.image_size,
                    "format": config.defaults.format
                }
            }
        }
    except Exception as e:
        logger.error(f"❌ Failed to load project: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load project: {str(e)}"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_project(request: CreateProjectRequest):
    """Create a new ModelCub project."""
    try:
        # Resolve path relative to WORKING_DIR
        if request.path:
            # If absolute path provided, use it
            if Path(request.path).is_absolute():
                project_path = request.path
            else:
                # Relative path: resolve from working dir
                project_path = str(WORKING_DIR / request.path)
        else:
            # Default: create in working dir
            project_path = str(WORKING_DIR / request.name)

        logger.info(f"📁 Creating project '{request.name}' at: {project_path}")
        logger.info(f"   Working dir: {WORKING_DIR}")

        req = InitProjectRequest(
            name=request.name,
            path=project_path,
            force=request.force
        )

        code, msg = init_project(req)

        if code != 0:
            logger.error(f"❌ Project creation failed: {msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg
            )

        logger.info(f"✅ Project created successfully at: {project_path}")

        return ApiResponse(
            success=True,
            message=f"Project '{request.name}' created successfully",
            data={
                "name": request.name,
                "path": project_path
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.delete("/{project_path:path}")
async def delete_project_route(project_path: str, body: DeleteProjectBody):
    """Delete a ModelCub project."""
    try:
        logger.info(f"🗑️  Deleting project: {project_path}")

        req = DeleteProjectRequest(
            target=project_path,
            yes=body.confirm
        )

        code, msg = delete_project(req)

        if code != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg
            )

        logger.info(f"✅ Project deleted: {project_path}")

        return ApiResponse(
            success=True,
            message="Project deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )

@router.post("/{project_path:path}/config")
async def set_project_config(project_path: str, request: SetConfigRequest):
    """Set a project configuration value."""
    try:
        from modelcub.sdk.project import Project

        logger.info(f"🔧 Setting config: {project_path} -> {request.key} = {request.value}")

        # Load project
        project = Project.load(project_path)

        # Validate key exists and is not project metadata
        if request.key.startswith("project."):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify project metadata (name, created, version)"
            )

        # Set value
        try:
            project.set_config(request.key, request.value)
            project.save_config()

            return ApiResponse(
                success=True,
                message=f"Configuration updated: {request.key} = {request.value}"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to set config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set config: {str(e)}"
        )