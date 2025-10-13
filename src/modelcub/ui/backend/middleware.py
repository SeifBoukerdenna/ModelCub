"""API middleware for request/response handling."""
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..shared.api.schemas import APIResponse, ErrorDetail, ResponseMeta
from ..shared.api.errors import APIError

logger = logging.getLogger(__name__)


class APIResponseMiddleware(BaseHTTPMiddleware):
    """Middleware to standardize API responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and standardize response."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Log request
        start_time = time.time()
        logger.info(
            f"[{request_id}] {request.method} {request.url.path}"
        )

        try:
            response = await call_next(request)

            # Log response time
            duration = time.time() - start_time
            logger.info(
                f"[{request_id}] {response.status_code} "
                f"({duration:.3f}s)"
            )

            return response

        except Exception as e:
            logger.error(
                f"[{request_id}] Error: {e}",
                exc_info=True
            )
            raise


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle errors and convert to standard format."""

    def _serialize_details(self, details: dict) -> dict:
        """Serialize error details, converting non-JSON-serializable types."""
        if not details:
            return {}

        serialized = {}
        for key, value in details.items():
            # Convert datetime to ISO string
            from datetime import datetime
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            # Convert Path to string
            elif hasattr(value, '__fspath__'):
                serialized[key] = str(value)
            # Keep primitives
            else:
                serialized[key] = value
        return serialized

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors and convert to standard API response."""
        try:
            return await call_next(request)
        except APIError as e:
            # Our custom API errors
            request_id = getattr(request.state, "request_id", None)

            error_response = APIResponse(
                success=False,
                data=None,
                error=ErrorDetail(
                    code=e.code,
                    message=e.message,
                    details=self._serialize_details(e.details) if e.details else None
                ),
                meta=ResponseMeta(request_id=request_id)
            )

            return JSONResponse(
                status_code=e.status_code,
                content=error_response.model_dump(exclude_none=True)
            )
        except Exception as e:
            # Unexpected errors
            request_id = getattr(request.state, "request_id", None)
            logger.error(f"Unexpected error: {e}", exc_info=True)

            error_response = APIResponse(
                success=False,
                data=None,
                error=ErrorDetail(
                    code="INTERNAL_ERROR",
                    message="Internal server error",
                    details={"error": str(e)}
                ),
                meta=ResponseMeta(request_id=request_id)
            )

            return JSONResponse(
                status_code=500,
                content=error_response.model_dump(exclude_none=True)
            )


class ProjectContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and validate project context."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Extract project path from header or query param."""
        # Get project path from header (backwards compatible)
        project_path = request.headers.get("X-Project-Path")

        # Or from query param
        if not project_path:
            project_path = request.query_params.get("project_path")

        # Store in request state
        request.state.project_path = project_path

        if project_path:
            logger.debug(f"Project context: {project_path}")

        return await call_next(request)