class AppError(Exception):
    """Base application error."""


class DataIngestError(AppError):
    """Raised when input data cannot be loaded."""
