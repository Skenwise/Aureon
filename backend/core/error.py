# backend/core/error.py

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

class NotFoundError(Exception):
    """
    Raised when a requested entity is not found in the database.
    """
    def __init__(self, entity: str, identifier: str):
        super().__init__(f"{entity} with identifier '{identifier}' not found")
        self.entity = entity
        self.identifier = identifier

class AuthenticationError(AureonError):
    """
    Exception raised for authentication failures.
    
    This includes:
    - Invalid credentials (username/password mismatch)
    - Expired tokens
    - Invalid tokens
    - Token signature verification failures
    """
    pass

class AuthorizationError(AureonError):
    """
    Exception raised for authorization failures.

    This is raised when an authenticated identity
    attempts to perform an action without the
    required permission or role authority.
    """
    pass

class CalculationError(AureonError):
    """
    Exception raised for errors during financial calculations.

    This includes:
    - Invalid input values (e.g., negative FX rates)
    - Division by zero or precision errors
    - Revaluation or conversion failures
    """
    pass

