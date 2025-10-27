# src/modelcub/__init__.py
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("modelcub")
except PackageNotFoundError:
    __version__ = "0.0.0+dev"

# Expose SDK
from .sdk import Project, Dataset, DatasetInfo, Box, Job, TrainingManager, TrainingRun

__all__ = ["Project", "Dataset", "DatasetInfo", "Box", "Job", "TrainingManager", "TrainingRun", "__version__"]