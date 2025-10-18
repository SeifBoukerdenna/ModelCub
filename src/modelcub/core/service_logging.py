"""
Structured logging for ModelCub services.
"""
import logging
import functools
from typing import Callable, Any
from .service_result import ServiceResult, ServiceTimer

logger = logging.getLogger("modelcub.services")


def log_service_call(operation: str):
    """
    Decorator to log service calls with timing and results.

    Usage:
        @log_service_call("init_project")
        def init_project(req: InitProjectRequest) -> ServiceResult[str]:
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> ServiceResult:
            timer = ServiceTimer()

            # Log start
            logger.info(f"[{operation}] Starting...")

            with timer:
                try:
                    result = func(*args, **kwargs)

                    # Add timing if ServiceResult
                    if isinstance(result, ServiceResult):
                        result.duration_ms = timer.elapsed_ms()

                    # Log result
                    if result.success:
                        logger.info(
                            f"[{operation}] Success ({timer.elapsed_ms():.2f}ms)",
                            extra={"duration_ms": timer.elapsed_ms(), "operation": operation}
                        )
                    else:
                        logger.warning(
                            f"[{operation}] Failed: {result.message} ({timer.elapsed_ms():.2f}ms)",
                            extra={"duration_ms": timer.elapsed_ms(), "operation": operation, "error": result.message}
                        )

                    return result

                except Exception as e:
                    logger.error(
                        f"[{operation}] Exception: {str(e)} ({timer.elapsed_ms():.2f}ms)",
                        exc_info=True,
                        extra={"duration_ms": timer.elapsed_ms(), "operation": operation, "exception": str(e)}
                    )
                    # Return error result
                    return ServiceResult.error(
                        message=f"Internal error: {str(e)}",
                        code=2,
                        duration_ms=timer.elapsed_ms()
                    )

        return wrapper
    return decorator