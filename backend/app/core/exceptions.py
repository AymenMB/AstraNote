"""
Custom exceptions for the application.
"""


class NotebookLMException(Exception):
    """Base exception for NotebookLM API errors."""
    
    def __init__(self, message: str, status_code: int = None, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ValidationException(Exception):
    """Exception for validation errors."""
    pass


class AuthenticationException(Exception):
    """Exception for authentication errors."""
    pass


class PermissionException(Exception):
    """Exception for permission errors."""
    pass


class DocumentProcessingException(Exception):
    """Exception for document processing errors."""
    pass


class QueryException(Exception):
    """Exception for query execution errors."""
    pass


class CacheException(Exception):
    """Exception for cache-related errors."""
    pass


class DatabaseException(Exception):
    """Exception for database-related errors."""
    pass
