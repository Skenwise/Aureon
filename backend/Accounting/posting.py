#backend/Accounting/posting.py
"""
Posting domain object.

Represents the atomic unit of accounting truth:
a transfer of value from one account to another.
Immutable, single-currency, and invariant-enforcing.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Optional
from core.money import Money
from core.error import DomainError
from schemas.postingSchema import PostingCreate


@dataclass(frozen=True)
class Posting:
    """
    Immutable ledger posting.

    Attributes:
        debit_account_id (UUID): Account to debit.
        credit_account_id (UUID): Account to credit.
        money (Money): Amount and currency being transferred.
        reference (Optional[str]): Optional reference for audit/tracking.
        timestamp (datetime): Time the posting was created.
    """

    debit_account_id: UUID
    credit_account_id: UUID
    money: Money
    reference: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

    def __post_init__(self) -> None:
        """Validate posting invariants after object creation."""
        if self.debit_account_id == self.credit_account_id:
            raise DomainError("Debit and credit accounts must differ")
        if self.money.amount <= 0:
            raise DomainError("Posting amount must be positive")
        if not self.money.currency or len(self.money.currency) != 3:
            raise DomainError("Posting must have a valid ISO 4217 currency code")

    @classmethod
    def from_schema(cls, schema: PostingCreate) -> "Posting":
        """
        Construct a Posting from a PostingCreate schema.

        Args:
            schema (PostingCreate): Schema containing posting data.

        Returns:
            Posting: Immutable posting object with validated invariants.
        """
        return cls(
            debit_account_id=schema.debit_account_id,
            credit_account_id=schema.credit_account_id,
            money=Money(amount=schema.amount, currency=schema.currency),
            reference=schema.reference,
            timestamp=schema.timestamp or datetime.utcnow(),
        )
