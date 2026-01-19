"""
Custom exception classes for the Aureon banking system.
These provide domain-specific error handling for different components.
"""


class AureonError(Exception):
    """Base exception class for all Aureon system errors."""
    pass


class LedgerError(AureonError):
    """Exception raised for errors in ledger operations."""
    pass


class TransactionError(AureonError):
    """Exception raised for errors in transaction processing."""
    pass


class ValidationError(AureonError):
    """Exception raised for validation failures."""
    pass


class LoanError(AureonError):
    """Exception raised for errors in loan operations."""
    pass
