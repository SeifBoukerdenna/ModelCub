"""
ModelCub exceptions.
"""


class ModelCubException(Exception):
    """Base exception for ModelCub."""
    pass


class ProjectNotFoundError(ModelCubException):
    """Raised when a project cannot be found."""
    pass


class DatasetNotFoundError(ModelCubException):
    """Raised when a dataset cannot be found."""
    pass


class DatasetExistsError(ModelCubException):
    """Raised when trying to create a dataset that already exists."""
    pass


class ClassExistsError(ModelCubException):
    """Raised when trying to add a class that already exists."""
    pass


class ClassNotFoundError(ModelCubException):
    """Raised when a class cannot be found."""
    pass


class InvalidConfigError(ModelCubException):
    """Raised when configuration is invalid."""
    pass


class InvalidDatasetError(ModelCubException):
    """Raised when dataset structure or format is invalid."""
    pass