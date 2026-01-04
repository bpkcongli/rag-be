class DomainError(Exception):
    """Base error for domain/application."""


class UnsupportedFileTypeError(DomainError):
    pass


class StorageError(DomainError):
    pass
