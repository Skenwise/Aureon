from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AccountID:
    """Immutable identifier for accounts."""
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("AccountID cannot be empty or whitespace-only")
        if not isinstance(self.value, str):
            raise TypeError("AccountID value must be a string")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, AccountID) and self.value == other.value


@dataclass(frozen=True)
class TransactionID:
    """Immutable identifier for transactions."""
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("TransactionID cannot be empty or whitespace-only")
        if not isinstance(self.value, str):
            raise TypeError("TransactionID value must be a string")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, TransactionID) and self.value == other.value


@dataclass(frozen=True)
class LoanID:
    """Immutable identifier for loans."""
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("LoanID cannot be empty or whitespace-only")
        if not isinstance(self.value, str):
            raise TypeError("LoanID value must be a string")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, LoanID) and self.value == other.value


@dataclass(frozen=True)
class CustomerID:
    """Immutable identifier for customers."""
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("CustomerID cannot be empty or whitespace-only")
        if not isinstance(self.value, str):
            raise TypeError("CustomerID value must be a string")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CustomerID) and self.value == other.value
