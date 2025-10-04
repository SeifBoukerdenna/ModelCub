from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Type, Any

# ---------- Event Types ----------
@dataclass(frozen=True)
class Event: ...

@dataclass(frozen=True)
class ProjectInitialized(Event):
    path: str
    name: str

@dataclass(frozen=True)
class ProjectDeleted(Event):
    path: str

@dataclass(frozen=True)
class DatasetAdded(Event):
    name: str
    path: str
    classes: list[str]

@dataclass(frozen=True)
class DatasetEdited(Event):
    name: str
    classes: list[str]

@dataclass(frozen=True)
class DatasetDeleted(Event):
    name: str
    path: str

@dataclass(frozen=True)
class GPUWarningSuppressed(Event):
    """Event fired when GPU warning is suppressed for the session."""
    pass

# ---------- Event Bus ----------
class EventBus:
    def __init__(self) -> None:
        self._subs: Dict[Type[Event], List[Callable[[Event], Any]]] = {}

    def subscribe(self, etype: Type[Event], fn: Callable[[Event], Any]) -> None:
        self._subs.setdefault(etype, []).append(fn)

    def publish(self, e: Event) -> None:
        for fn in self._subs.get(type(e), []):
            fn(e)

# Global, simple bus (replace with DI if you want)
bus = EventBus()