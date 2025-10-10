# src/modelcub/__init__.py
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("modelcub")
except PackageNotFoundError:
    __version__ = "0.0.0+dev"

# Expose SDK
from .sdk import Project

__all__ = ["Project", "__version__"]