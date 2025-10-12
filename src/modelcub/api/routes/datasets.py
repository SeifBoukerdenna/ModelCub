"""Dataset management API routes (placeholder)."""
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