"""
Adapter to convert ServiceResult to APIResponse for FastAPI routes.
"""
from typing import TypeVar, Callable, Any
from functools import wraps
import logging

from ...shared.api.schemas import APIResponse, ResponseMeta
from ...shared.api.errors import APIError
from ....core.service_result import ServiceResult

T = TypeVar('T')
logger = logging.getLogger(__name__)


def service_to_api(func: Callable) -> Callable:
    """
    Decorator to convert ServiceResult to APIResponse.

    Usage:
        @router.post("/projects")
        @service_to_api
        async def create_project(req: CreateRequest) -> ServiceResult[Project]:
            return project_service.init_project(req)
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> APIResponse:
        # Call the service function
        if hasattr(func, '__wrapped__'):
            result = await func.__wrapped__(*args, **kwargs)
        else:
            result = await func(*args, **kwargs)

        # Handle ServiceResult
        if isinstance(result, ServiceResult):
            if not result.success:
                # Convert to API error
                raise APIError(
                    message=result.message,
                    status_code=400 if result.code == 2 else 500,
                    code=f"SERVICE_ERROR_{result.code}",
                    details=result.metadata
                )

            # Success response
            return APIResponse(
                success=True,
                data=result.data,
                message=result.message,
                meta=ResponseMeta(
                    duration_ms=result.duration_ms,
                    **result.metadata
                )
            )

        # Pass through if not ServiceResult
        return result

    return wrapper


class ServiceAdapter:
    """Helper to call services from API routes."""

    @staticmethod
    def call_sync(service_func: Callable, *args, **kwargs) -> APIResponse[T]:
        """
        Call synchronous service function and convert result to APIResponse.

        Usage:
            result = ServiceAdapter.call_sync(init_project, req)
        """
        try:
            result = service_func(*args, **kwargs)

            if isinstance(result, ServiceResult):
                if not result.success:
                    raise APIError(
                        message=result.message,
                        status_code=400 if result.code == 2 else 500,
                        code=f"SERVICE_ERROR_{result.code}",
                        details=result.metadata
                    )

                return APIResponse(
                    success=True,
                    data=result.data,
                    message=result.message,
                    meta=ResponseMeta(
                        duration_ms=result.duration_ms,
                        **result.metadata
                    )
                )

            # Fallback for non-ServiceResult
            return APIResponse(success=True, data=result)

        except APIError:
            raise
        except Exception as e:
            logger.error(f"Service call failed: {e}", exc_info=True)
            raise APIError(
                message=str(e),
                status_code=500,
                code="INTERNAL_ERROR"
            )