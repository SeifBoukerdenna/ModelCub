"""
Training events for ModelCub event system.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class TrainingRunCreated:
    """Emitted when a training run is created."""
    run_id: str
    dataset_name: str
    model: str
    epochs: int
    device: str


@dataclass
class TrainingStarted:
    """Emitted when training starts."""
    run_id: str
    pid: int
    dataset_name: str
    model: str


@dataclass
class TrainingCompleted:
    """Emitted when training completes successfully."""
    run_id: str
    duration_ms: int
    metrics: Dict[str, Any]
    best_weights_path: Optional[str]


@dataclass
class TrainingFailed:
    """Emitted when training fails."""
    run_id: str
    error: str
    duration_ms: Optional[int]


@dataclass
class TrainingCancelled:
    """Emitted when training is cancelled by user."""
    run_id: str
    pid: Optional[int]


@dataclass
class TrainingProgress:
    """Emitted periodically during training (future)."""
    run_id: str
    epoch: int
    total_epochs: int
    loss: Optional[float]


@dataclass
class OrphanedProcessRecovered:
    """Emitted when an orphaned process is detected and cleaned up."""
    run_id: str
    pid: int