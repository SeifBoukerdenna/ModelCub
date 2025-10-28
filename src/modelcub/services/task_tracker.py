"""
ModelCub Task Resource Tracker
Tracks resource usage of specific ModelCub operations (training, annotation, data processing)
"""

import psutil
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ModelCubTask:
    """Represents an active ModelCub task"""
    task_id: str
    task_type: str  # 'training', 'annotation', 'data_processing', 'inference'
    name: str
    pid: int
    started_at: datetime
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    gpu_memory_mb: float = 0.0


class TaskResourceTracker:
    """Singleton tracker for ModelCub tasks"""
    _instance = None
    _tasks: Dict[str, ModelCubTask] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register_task(self, task_id: str, task_type: str, name: str, pid: int) -> None:
        """Register a new ModelCub task"""
        self._tasks[task_id] = ModelCubTask(
            task_id=task_id,
            task_type=task_type,
            name=name,
            pid=pid,
            started_at=datetime.now()
        )

    def unregister_task(self, task_id: str) -> None:
        """Remove a task when it completes"""
        self._tasks.pop(task_id, None)

    def update_resources(self) -> None:
        """Update resource usage for all tracked tasks"""
        for task_id, task in list(self._tasks.items()):
            try:
                proc = psutil.Process(task.pid)
                task.cpu_percent = proc.cpu_percent(interval=0.1)
                task.memory_mb = proc.memory_info().rss / 1024 / 1024

                # GPU tracking would need GPU process mapping
                # This is complex - requires nvidia-ml-py and process matching

            except psutil.NoSuchProcess:
                # Process ended, remove task
                self.unregister_task(task_id)
            except Exception as e:
                print(f"Error updating task {task_id}: {e}")

    def get_active_tasks(self) -> List[ModelCubTask]:
        """Get all active tasks sorted by resource usage"""
        self.update_resources()
        return sorted(
            self._tasks.values(),
            key=lambda t: t.cpu_percent + (t.memory_mb / 1000),
            reverse=True
        )

    def get_task_by_id(self, task_id: str) -> Optional[ModelCubTask]:
        """Get specific task by ID"""
        return self._tasks.get(task_id)


# Global tracker instance
tracker = TaskResourceTracker()


# Helper function for easy access
def get_tracker() -> TaskResourceTracker:
    """Get the global task tracker instance"""
    return tracker