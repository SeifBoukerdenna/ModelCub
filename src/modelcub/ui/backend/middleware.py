"""Middleware - don't strip meta field."""
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
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.time()

        logger.info(f"[{request_id}] {request.method} {request.url.path}")

        try:
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info(f"[{request_id}] {response.status_code} ({duration:.3f}s)")
            return response
        except Exception as e:
            logger.error(f"[{request_id}] Error: {e}", exc_info=True)
            raise

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    def _serialize_details(self, details: dict) -> dict:
        if not details:
            return {}
        serialized = {}
        for key, value in details.items():
            from datetime import datetime
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif hasattr(value, '__fspath__'):
                serialized[key] = str(value)
            else:
                serialized[key] = value
        return serialized

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except APIError as e:
            request_id = getattr(request.state, "request_id", None)
            error_response = APIResponse(
                success=False,
                data=None,
                error=ErrorDetail(
                    code=e.code,
                    message=e.message,
                    details=self._serialize_details(e.details) if e.details else None
                ),
                meta=ResponseMeta(request_id=request_id)  # CRITICAL: Include meta
            )
            return JSONResponse(
                status_code=e.status_code,
                content=error_response.model_dump(exclude_none=False)  # Don't exclude meta
            )
        except Exception as e:
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
                meta=ResponseMeta(request_id=request_id)  # CRITICAL: Include meta
            )
            return JSONResponse(
                status_code=500,
                content=error_response.model_dump(exclude_none=False)  # Don't exclude meta
            )

class ProjectContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        project_path = request.headers.get("X-Project-Path")
        if not project_path:
            project_path = request.query_params.get("project_path")
        request.state.project_path = project_path
        if project_path:
            logger.debug(f"Project context: {project_path}")
        return await call_next(request)
