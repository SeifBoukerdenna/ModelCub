"""FastAPI application for ModelCub UI with WebSocket support."""
from pathlib import Path
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .routes import projects, datasets, models, jobs, annotations, runs
from .websockets import ConnectionManager
from .middleware import APIResponseMiddleware, ErrorHandlerMiddleware, ProjectContextMiddleware
from ..shared.api.config import APIConfig, Endpoints
from ..shared.api.schemas import APIResponse

from ...core.logging_config import setup_logging


setup_logging()

# Configure uvicorn logger
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)


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
    version=APIConfig.VERSION,
    docs_url=f"{APIConfig.PREFIX}/docs",
    redoc_url=f"{APIConfig.PREFIX}/redoc",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(ProjectContextMiddleware)
app.add_middleware(APIResponseMiddleware)

# WebSocket connection manager
manager = ConnectionManager()

# Inject WebSocket manager into jobs router
jobs.set_websocket_manager(manager)

# Include API routers
app.include_router(projects.router, prefix=APIConfig.PREFIX)
app.include_router(datasets.router, prefix=APIConfig.PREFIX)
app.include_router(models.router, prefix=APIConfig.PREFIX)
app.include_router(jobs.router, prefix=APIConfig.PREFIX)
app.include_router(annotations.router, prefix=APIConfig.PREFIX)
app.include_router(runs.router, prefix=APIConfig.PREFIX)


@app.get(f"{APIConfig.PREFIX}{Endpoints.HEALTH}")
async def health_check() -> APIResponse[dict]:
    """Health check endpoint."""
    return APIResponse(
        success=True,
        data={
            "status": "healthy",
            "service": "modelcub-api",
            "version": APIConfig.VERSION
        }
    )


@app.websocket(Endpoints.WS)
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time job updates."""
    client_id = await manager.connect(websocket)
    logger.info(f"WebSocket client {client_id} connected")

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()

            # Echo back for heartbeat
            if data == "ping":
                await manager.send_to_client(client_id, {"type": "pong"})
            else:
                logger.debug(f"Received from {client_id}: {data}")

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"WebSocket client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}", exc_info=True)
        manager.disconnect(client_id)


# Serve frontend in production
FRONTEND_BUILD_DIR = Path(__file__).parent.parent / "frontend" / "dist"

if FRONTEND_BUILD_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_BUILD_DIR / "assets"),
        name="assets"
    )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React SPA with client-side routing."""
        if full_path.startswith("api/"):
            return {"error": "Not found"}, 404

        file_path = FRONTEND_BUILD_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        index_path = FRONTEND_BUILD_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        return {"error": "Not found"}, 404


def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False
) -> None:
    """Run the FastAPI server with uvicorn."""
    import uvicorn

    logger.info(f"🚀 Starting ModelCub API at http://{host}:{port}")
    logger.info(f"📚 API Documentation: http://{host}:{port}{APIConfig.PREFIX}/docs")
    logger.info(f"🔌 WebSocket endpoint: ws://{host}:{port}/ws")

    if reload:
        logger.info("🔄 Auto-reload enabled")

    uvicorn.run(
        "modelcub.ui.backend.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )