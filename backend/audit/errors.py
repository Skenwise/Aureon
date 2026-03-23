#backend/audit/errors.py

"""
Audit Module Errors.

Defines domain-specific exceptions for audit operations.
"""


class AuditError(Exception):
    """Base exception for audit module errors."""
    pass


class AuditLogError(AuditError):
    """Raised when audit log operation fails."""
    pass


class ReconciliationError(AuditError):
    """Raised when reconciliation operation fails."""
    pass