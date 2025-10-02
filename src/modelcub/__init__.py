# src/modelcub/__init__.py
from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("modelcub")
except PackageNotFoundError:  # e.g. when running from source without install
    __version__ = "0.0.0+dev"
