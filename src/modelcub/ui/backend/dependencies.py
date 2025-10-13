"""FastAPI dependencies for dependency injection."""
import os
import logging
from pathlib import Path
from typing import Optional, Annotated

from fastapi import Request, Depends, Header

from modelcub.sdk.project import Project
from ..shared.api.errors import NotFoundError, ProjectError, ErrorCode

logger = logging.getLogger(__name__)

# Get working directory
WORKING_DIR = Path(os.environ.get("MODELCUB_WORKING_DIR", Path.cwd()))


def get_working_dir() -> Path:
    """Get the working directory."""
    return WORKING_DIR


def get_request_id(request: Request) -> Optional[str]:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", None)


def get_project_path_from_request(
    request: Request,
    x_project_path: Optional[str] = Header(None)
) -> Optional[str]:
    """Get project path from request (header or state)."""
    # Try header first (backwards compatible)
    if x_project_path:
        return x_project_path

    # Try request state (set by middleware)
    return getattr(request.state, "project_path", None)


def get_project_path_required(
    project_path: Optional[str] = Depends(get_project_path_from_request)
) -> str:
    """Get project path - required (raises error if not provided)."""
    if not project_path:
        raise ProjectError(
            message="Project path is required. Provide via X-Project-Path header or project_path query param.",
            code=ErrorCode.PROJECT_NOT_FOUND
        )
    return project_path


def load_project(
    project_path: Optional[str] = Depends(get_project_path_from_request),
    working_dir: Path = Depends(get_working_dir)
) -> Optional[Project]:
    """Load project from path (returns None if not provided)."""
    if not project_path:
        return None

    try:
        # Resolve path
        full_path = Path(project_path)
        if not full_path.is_absolute():
            full_path = working_dir / project_path

        # Check if project exists
        if not (full_path / ".modelcub").exists():
            raise NotFoundError(
                message=f"Project not found at: {full_path}",
                code=ErrorCode.PROJECT_NOT_FOUND
            )

        # Load project
        logger.debug(f"Loading project from: {full_path}")
        return Project.load(str(full_path))

    except (NotFoundError, ProjectError):
        raise
    except Exception as e:
        logger.error(f"Failed to load project: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to load project: {str(e)}",
            code=ErrorCode.PROJECT_LOAD_FAILED,
            details={"path": str(project_path), "error": str(e)}
        )


def load_project_required(
    project_path: str = Depends(get_project_path_required),
    working_dir: Path = Depends(get_working_dir)
) -> Project:
    """Load project - required (raises error if not found)."""
    try:
        # Resolve path
        full_path = Path(project_path)
        if not full_path.is_absolute():
            full_path = working_dir / project_path

        # Check if project exists
        if not (full_path / ".modelcub").exists():
            raise NotFoundError(
                message=f"Project not found at: {full_path}",
                code=ErrorCode.PROJECT_NOT_FOUND
            )

        # Load project
        logger.debug(f"Loading project from: {full_path}")
        return Project.load(str(full_path))

    except (NotFoundError, ProjectError):
        raise
    except Exception as e:
        logger.error(f"Failed to load project: {e}", exc_info=True)
        raise ProjectError(
            message=f"Failed to load project: {str(e)}",
            code=ErrorCode.PROJECT_LOAD_FAILED,
            details={"path": str(project_path), "error": str(e)}
        )


# Type aliases for cleaner endpoint signatures
ProjectPath = Annotated[Optional[str], Depends(get_project_path_from_request)]
ProjectPathRequired = Annotated[str, Depends(get_project_path_required)]
ProjectOptional = Annotated[Optional[Project], Depends(load_project)]
ProjectRequired = Annotated[Project, Depends(load_project_required)]
WorkingDir = Annotated[Path, Depends(get_working_dir)]
RequestId = Annotated[Optional[str], Depends(get_request_id)]