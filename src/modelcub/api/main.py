"""FastAPI application for ModelCub UI."""
from typing import Optional
from pathlib import Path
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
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
    # Automatically redirect trailing slashes
    redirect_slashes=True
)

# Add middleware to handle trailing slashes consistently
@app.middleware("http")
async def redirect_trailing_slash(request: Request, call_next):
    """Redirect requests without trailing slash to with trailing slash for consistency."""
    path = request.url.path

    # Skip static files and websocket
    if path.startswith("/assets") or path == "/ws":
        return await call_next(request)

    # If it's an API route without trailing slash and not a specific resource
    if path.startswith("/api/") and not path.endswith("/"):
        # Check if it's a list endpoint (not /api/projects/123)
        parts = path.split("/")
        # If the last part is a known collection endpoint, redirect
        if parts[-1] in ["projects", "datasets", "models", "health"]:
            return RedirectResponse(
                url=str(request.url).replace(path, f"{path}/"),
                status_code=status.HTTP_308_PERMANENT_REDIRECT
            )

    return await call_next(request)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Vite dev server
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
            # Echo back for now
            await manager.send_to_client(client_id, {"echo": data})
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(client_id)


# Serve built UI in production
UI_BUILD_DIR = Path(__file__).parent / "static"

if UI_BUILD_DIR.exists():
    # Serve static assets
    app.mount(
        "/assets",
        StaticFiles(directory=UI_BUILD_DIR / "assets"),
        name="assets"
    )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React SPA with client-side routing support."""
        file_path = UI_BUILD_DIR / full_path

        # Serve file if it exists
        if file_path.is_file():
            return FileResponse(file_path)

        # Otherwise serve index.html for client-side routing
        index_path = UI_BUILD_DIR / "index.html"
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
    """Run the FastAPI server with uvicorn.

    Args:
        host: Server host address
        port: Server port
        reload: Enable auto-reload for development
    """
    import uvicorn

    logger.info(f"🚀 Starting ModelCub API at http://{host}:{port}")
    if reload:
        logger.info("🔄 Auto-reload enabled")

    uvicorn.run(
        "modelcub.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )