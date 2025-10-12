"""Custom exception hierarchy for ModelCub."""


class ModelCubException(Exception):
    """Base exception for all ModelCub errors."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ProjectException(ModelCubException):
    """Project-related errors."""
    pass


class ProjectNotFoundError(ProjectException):
    """Project does not exist."""
    pass


class ProjectAlreadyExistsError(ProjectException):
    """Project already exists."""
    pass


class DatasetException(ModelCubException):
    """Dataset-related errors."""
    pass


class DatasetNotFoundError(DatasetException):
    """Dataset does not exist."""
    pass


class ModelException(ModelCubException):
    """Model-related errors."""
    pass


class TrainingException(ModelException):
    """Training-related errors."""
    pass


class ValidationException(ModelCubException):
    """Validation errors."""
    pass


class ConfigurationError(ModelCubException):
    """Configuration errors."""
    pass


class ImportException(ModelCubException):
    """Import-related errors."""
    pass


class AnnotationException(ModelCubException):
    """Annotation-related errors."""
    pass