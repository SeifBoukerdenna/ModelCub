"""
ModelCub SDK - Programmatic Interface.

Complete Python API for ModelCub projects, datasets, training, and jobs.
"""

from .project import Project
from .dataset import Dataset, DatasetInfo, Box
from .job import JobManager, Job, JobStatus, TaskStatus
from .training_run import TrainingRun, TrainingManager, RunMetrics

__all__ = [
    # Project
    "Project",

    # Dataset
    "Dataset",
    "DatasetInfo",
    "Box",

    # Jobs
    "JobManager",
    "Job",
    "JobStatus",
    "TaskStatus",

    # Training
    "TrainingRun",
    "TrainingManager",
    "RunMetrics",
]