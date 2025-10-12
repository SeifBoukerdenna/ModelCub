"""Project management API routes."""
from typing import Optional, List
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from modelcub.services.project_service import (
    init_project,
    delete_project,
    InitProjectRequest,
    DeleteProjectRequest
)
from modelcub.core.config import load_config

router = APIRouter(prefix="/api/projects")


# Request/Response models
class CreateProjectRequest(BaseModel):
    """Request model for creating a project."""
    name: str = Field(..., min_length=1, max_length=100)
    path: Optional[str] = None
    force: bool = False


class DeleteProjectBody(BaseModel):
    """Request body for deleting a project."""
    confirm: bool = False


class ProjectInfo(BaseModel):
    """Project information model."""
    name: str
    path: str
    created: str
    version: str
    config: dict


class ProjectListItem(BaseModel):
    """Project list item."""
    name: str
    path: str
    created: str
    is_current: bool


class ApiResponse(BaseModel):
    """Standard API response."""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


# Helper function to find all projects
def find_projects(search_path: Path = Path.cwd()) -> List[ProjectListItem]:
    """Find all ModelCub projects in current directory and subdirectories."""
    projects = []
    current_path = Path.cwd()

    # Check current directory
    if (search_path / ".modelcub").exists():
        config = load_config(search_path)
        if config:
            projects.append(ProjectListItem(
                name=config.project.name,
                path=str(search_path),
                created=config.project.created,
                is_current=search_path == current_path
            ))

    # Check subdirectories (one level deep)
    try:
        for item in search_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                if (item / ".modelcub").exists():
                    config = load_config(item)
                    if config:
                        projects.append(ProjectListItem(
                            name=config.project.name,
                            path=str(item),
                            created=config.project.created,
                            is_current=item == current_path
                        ))
    except PermissionError:
        pass

    return projects


# Routes
@router.get("/", response_model=dict)
async def list_projects():
    """List all ModelCub projects in current directory."""
    try:
        projects = find_projects()
        return {
            "success": True,
            "projects": [p.model_dump() for p in projects],
            "count": len(projects)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )


@router.get("/current", response_model=dict)
async def get_current_project():
    """Get current project information."""
    try:
        config = load_config(Path.cwd())

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
                "path": str(Path.cwd()),
                "config": {
                    "device": config.defaults.device,
                    "batch_size": config.defaults.batch_size,
                    "image_size": config.defaults.image_size,
                    "format": config.defaults.format
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load project: {str(e)}"
        )


@router.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_project(request: CreateProjectRequest):
    """Create a new ModelCub project."""
    try:
        req = InitProjectRequest(
            name=request.name,
            path=request.path or f"./{request.name}",
            force=request.force
        )

        code, msg = init_project(req)

        if code != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg
            )

        return ApiResponse(
            success=True,
            message=f"Project '{request.name}' created successfully",
            data={
                "name": request.name,
                "path": req.path
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.delete("/{project_path:path}", response_model=ApiResponse)
async def delete_project_route(project_path: str, body: DeleteProjectBody):
    """Delete a ModelCub project."""
    try:
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

        return ApiResponse(
            success=True,
            message="Project deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )