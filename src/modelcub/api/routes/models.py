"""Model training API routes (placeholder)."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/models")


@router.get("/")
async def list_models():
    """List available models."""
    return {
        "success": True,
        "models": [],
        "message": "Model operations coming soon"
    }