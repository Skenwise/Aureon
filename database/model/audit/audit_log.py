# models/audit/audit_log.py
from sqlmodel import SQLModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from ..base import BaseModel

class AuditLog(BaseModel, table=True):
    """
    Immutable audit log for all sensitive actions
    (who did what, when, and from where)
    """
    entity: str = Field(..., max_length=100)       # e.g. "loan", "account", "journal"
    entity_id: UUID
    action: str = Field(..., max_length=50)        # create, update, approve, reverse

    performed_by: Optional[UUID] = Field(
        foreign_key="user.id", default=None
    )

    performed_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    changes: Optional[str] = Field(default=None)   # JSON diff
    metadata_: Optional[str] = Field(default=None)