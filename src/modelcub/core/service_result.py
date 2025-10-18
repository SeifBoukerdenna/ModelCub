"""
Unified service response pattern with timing and metadata.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, TypeVar, Generic, Dict
from datetime import datetime
import time

T = TypeVar('T')


@dataclass
class ServiceResult(Generic[T]):
    """
    Standard result object for all service operations.

    Attributes:
        success: Whether the operation succeeded
        message: Human-readable message
        data: Optional result data (can be any type)
        code: Exit code (0 for success, non-zero for errors)
        duration_ms: Operation duration in milliseconds
        timestamp: When the operation completed
        metadata: Additional metadata (warnings, debug info, etc.)
    """
    success: bool
    message: str = ""
    data: Optional[T] = None
    code: int = 0
    duration_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(
        cls,
        data: Optional[T] = None,
        message: str = "",
        duration_ms: float = 0.0,
        **metadata
    ) -> ServiceResult[T]:
        """Create a successful result."""
        return cls(
            success=True,
            message=message,
            data=data,
            code=0,
            duration_ms=duration_ms,
            metadata=metadata
        )

    @classmethod
    def error(
        cls,
        message: str,
        code: int = 1,
        data: Optional[T] = None,
        duration_ms: float = 0.0,
        **metadata
    ) -> ServiceResult[T]:
        """Create an error result."""
        return cls(
            success=False,
            message=message,
            data=data,
            code=code,
            duration_ms=duration_ms,
            metadata=metadata
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "code": self.code,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


class ServiceTimer:
    """Context manager for timing service operations."""

    def __init__(self):
        self.start_time = None
        self.duration_ms = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            self.duration_ms = (time.perf_counter() - self.start_time) * 1000
        return False

    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        if self.start_time:
            return (time.perf_counter() - self.start_time) * 1000
        return 0.0