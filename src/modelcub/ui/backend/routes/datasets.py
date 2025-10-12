"""Dataset management API routes (placeholder for future)."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/datasets")


@router.get("/")
async def list_datasets():
    """List datasets in current project."""
    return {
        "success": True,
        "datasets": [],
        "message": "Dataset operations coming soon"
    }