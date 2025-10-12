"""
ModelCub SDK - Programmatic Interface.

Import classes directly:
    from modelcub import Project, Dataset

Or from SDK package:
    from modelcub.sdk import Project, Dataset
"""

from .project import Project
from .dataset import Dataset, DatasetInfo

__all__ = ["Project", "Dataset", "DatasetInfo"]