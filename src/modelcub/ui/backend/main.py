"""FastAPI application for ModelCub UI."""
from pathlib import Path
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .routes import projects, datasets, models
from .websockets import ConnectionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ModelCub API",
    description="Local-first computer vision platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
manager = ConnectionManager()


# Custom exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error"
        }
    )


# @app.get("/api/datasets/")
# async def get_datasets():
#     """TEST"""
#     return {
#         "success": True,
#         "datasets": [],
#         "count": -10,
#         "message": "LMFAOOO -- API"
#     }


# Include API routers
app.include_router(projects.router, tags=["Projects"])
app.include_router(datasets.router, tags=["Datasets"])
app.include_router(models.router, tags=["Models"])


# Health check
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "modelcub-api",
        "version": "1.0.0"
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time updates."""
    client_id = await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received from {client_id}: {data}")
            await manager.send_to_client(client_id, {"echo": data})
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(client_id)


# Serve built UI in production
FRONTEND_BUILD_DIR = Path(__file__).parent.parent / "frontend" / "dist"

if FRONTEND_BUILD_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_BUILD_DIR / "assets"),
        name="assets"
    )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React SPA with client-side routing support."""
        file_path = FRONTEND_BUILD_DIR / full_path

        if file_path.is_file():
            return FileResponse(file_path)

        index_path = FRONTEND_BUILD_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        return JSONResponse(
            status_code=404,
            content={"error": "Not found"}
        )


def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False
) -> None:
    """Run the FastAPI server with uvicorn."""
    import uvicorn

    logger.info(f"🚀 Starting ModelCub API at http://{host}:{port}")
    if reload:
        logger.info("🔄 Auto-reload enabled")

    uvicorn.run(
        "modelcub.ui.backend.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )