# models/finance/posting.py
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import Optional, TYPE_CHECKING
from ..base import BaseModel

# only import for type checking to avoid circular imports
if TYPE_CHECKING:
    from .account import Account
    from .journal import Journal

class Posting(BaseModel, table=True):
    """
    Represents a single entry in a ledger journal (debit or credit)
    """
    journal_id: UUID = Field(foreign_key="journal.id", index=True)
    account_id: UUID = Field(foreign_key="account.id", index=True)
    amount: float = Field(...)
    entry_type: str = Field(..., max_length=10)  # "debit" or "credit"
    currency: str = Field(foreign_key="currency.code", max_length=3)
    description: Optional[str] = Field(default=None)
    metadata_: Optional[str] = Field(default=None)

    # Relationships
    journal: Optional["Journal"] = Relationship(back_populates="postings")
    account: Optional["Account"] = Relationship(back_populates="postings")