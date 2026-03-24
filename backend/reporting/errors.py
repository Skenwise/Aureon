"""
Reporting Module Errors.

Defines domain-specific exceptions for reporting operations.
"""


class ReportingError(Exception):
    """Base exception for reporting module errors."""
    pass


class ReportGenerationError(ReportingError):
    """Raised when report generation fails."""
    pass


class ReportNotFoundError(ReportingError):
    """Raised when a requested report is not found."""
    pass