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
        foreign_key="user.id", default=None,
        description="The ID of the user who performed the action"
    )

    performed_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(default=None, max_length=45, description="The IP address from which the action was performed")
    changes: Optional[str] = Field(default=None, description="JSON-encoded changes made during the action")
    metadata_: Optional[str] = Field(default=None, description="Additional metadata")

    @validator('entity')
    def validate_entity(cls, v):
        """
        Validates that the entity is a non-empty string with a maximum length of 100 characters.
        """
        if not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("Entity must be a non-empty string")
        if len(v) > 100:
            raise ValueError("Entity cannot exceed 100 characters")
        return v

    @validator('action')
    def validate_action(cls, v):
        """
        Validates that the action is a non-empty string with a maximum length of 50 characters.
        """
        if not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("Action must be a non-empty string")
        if len(v) > 50:
            raise ValueError("Action cannot exceed 50 characters")
        return v

    @validator('ip_address')
    def validate_ip_address(cls, v):
        """
        Validates that the IP address is a valid IPv4 or IPv6 address.
        """
        import ipaddress
        if v is not None and not isinstance(v, str):
            raise ValueError("IP address must be a string")
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError("Invalid IP address format")
        return v

    @validator('changes')
    def validate_changes(cls, v):
        """
        Validates that the changes are valid JSON.
        """
        import json
        if v is not None and not isinstance(v, str):
            raise ValueError("Changes must be a string")
        try:
            json.loads(v)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for changes")
        return v

    @validator('metadata_')
    def validate_metadata(cls, v):
        """
        Validates that the metadata is valid JSON.
        """
        import json
        if v is not None and not isinstance(v, str):
            raise ValueError("Metadata must be a string")
        try:
            json.loads(v)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for metadata")
        return v
