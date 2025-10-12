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
from modelcub.core.config import load_config, save_config
from modelcub.sdk.project import Project

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
    workers: int
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
                    workers=config.defaults.workers,
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
                                workers=config.defaults.workers,
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
                    "workers": config.defaults.workers,
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


@router.get("/config")
async def get_project_config(path: str):
    """Get configuration for a specific project by path."""
    try:
        # Resolve path
        full_path = Path(path)
        if not full_path.is_absolute():
            full_path = WORKING_DIR / path

        logger.info(f"⚙️  Loading config from: {full_path}")

        # Check if project exists
        if not (full_path / ".modelcub").exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found at: {full_path}"
            )

        # Load config directly (don't use SDK Project class)
        config = load_config(full_path)

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuration not found at: {full_path}"
            )

        return {
            "success": True,
            "config": {
                "project": {
                    "name": config.project.name,
                    "created": config.project.created,
                    "version": config.project.version
                },
                "defaults": {
                    "device": config.defaults.device,
                    "batch_size": config.defaults.batch_size,
                    "image_size": config.defaults.image_size,
                    "workers": config.defaults.workers,
                    "format": config.defaults.format
                },
                "paths": {
                    "data": config.paths.data,
                    "runs": config.paths.runs,
                    "reports": config.paths.reports
                }
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to load config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load config: {str(e)}"
        )


@router.post("/config")
async def set_project_config(path: str, request: SetConfigRequest):
    """Set a configuration value for a specific project."""
    try:
        # Resolve path
        full_path = Path(path)
        if not full_path.is_absolute():
            full_path = WORKING_DIR / path

        logger.info(f"⚙️  Setting config for: {full_path}")
        logger.info(f"    {request.key} = {request.value}")

        # Check if project exists
        if not (full_path / ".modelcub").exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project not found at: {full_path}"
            )

        # Prevent changing project metadata
        if request.key.startswith("project."):
            logger.warning(f"⚠️  Attempted to modify immutable project metadata: {request.key}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify project metadata (name, created, version). These fields are immutable."
            )

        # Load config
        config = load_config(full_path)
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Configuration not found at: {full_path}"
            )

        # Get old value for logging
        parts = request.key.split(".")
        if len(parts) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid key format: {request.key}. Use format 'section.key' (e.g. 'defaults.device')"
            )

        section, key = parts

        # Validate section and key exist
        if section == "defaults":
            if not hasattr(config.defaults, key):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid key: {request.key}. Available: defaults.device, defaults.batch_size, defaults.image_size, defaults.workers"
                )
            old_value = getattr(config.defaults, key)
            setattr(config.defaults, key, request.value)
        elif section == "paths":
            if not hasattr(config.paths, key):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid key: {request.key}. Available: paths.data, paths.runs, paths.reports"
                )
            old_value = getattr(config.paths, key)
            setattr(config.paths, key, request.value)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid section: {section}. Use 'defaults' or 'paths'"
            )

        # Save config
        save_config(full_path, config)

        logger.info(f"✅ Config updated: {request.key}: {old_value} → {request.value}")

        return {
            "success": True,
            "message": f"Configuration updated successfully",
            "data": {
                "key": request.key,
                "old_value": old_value,
                "new_value": request.value
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to set config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set config: {str(e)}"
        )