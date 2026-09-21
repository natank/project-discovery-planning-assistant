"""Application error types."""


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is unavailable or invalid."""


class StorageError(RuntimeError):
    """Raised when project state or artifacts cannot be safely persisted."""
