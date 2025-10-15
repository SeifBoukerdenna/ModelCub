"""
Event system for ModelCub.
"""
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ProjectInitialized:
    path: str
    name: str


@dataclass
class ProjectDeleted:
    path: str


@dataclass
class DatasetImported:
    name: str
    path: str
    image_count: int
    source: str


@dataclass
class DatasetAdded:
    name: str
    path: str


@dataclass
class DatasetEdited:
    name: str
    old_name: str | None


@dataclass
class DatasetDeleted:
    name: str
    path: str

@dataclass
class AnnotationSaved:
    dataset_name: str
    image_id: str
    num_boxes: int

@dataclass
class AnnotationDeleted:
    dataset_name: str
    image_id: str


class EventBus:
    """Simple event bus for internal events."""

    def __init__(self):
        self._handlers: dict[type, list[Callable]] = {}

    def subscribe(self, event_type: type, handler: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: Any) -> None:
        """Publish an event to all subscribers."""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception:
                    pass  # Silent failure for now


# Global event bus instance
bus = EventBus()