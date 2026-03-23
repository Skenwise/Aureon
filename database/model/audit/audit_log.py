# models/audit/audit_log.py
from sqlmodel import SQLModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import field_validator
import ipaddress
import json
from ..base import BaseModel


class AuditLog(BaseModel, table=True):
    """
    Immutable audit log for all sensitive actions
    (who did what, when, and from where)
    """
    # Tenant isolation — CRITICAL for multi-tenancy
    tenant_id: UUID = Field(foreign_key="company.id", nullable=False, index=True)
    
    entity: str = Field(..., max_length=100)       # e.g. "loan", "account", "journal"
    entity_id: UUID = Field(index=True)
    action: str = Field(..., max_length=50)        # create, update, approve, reverse

    performed_by: Optional[UUID] = Field(
        foreign_key="user.id", default=None,
        description="The ID of the user who performed the action"
    )

    performed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    ip_address: Optional[str] = Field(default=None, max_length=45)
    changes: Optional[str] = Field(default=None, description="JSON-encoded changes")
    metadata_: Optional[str] = Field(default=None, description="Additional metadata")

    # ==================== VALIDATORS ====================

    @field_validator('entity', mode='before')
    @classmethod
    def validate_entity(cls, v):
        if v is None:
            raise ValueError("Entity cannot be None")
        if not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("Entity must be a non-empty string")
        if len(v) > 100:
            raise ValueError("Entity cannot exceed 100 characters")
        return v.strip()

    @field_validator('action', mode='before')
    @classmethod
    def validate_action(cls, v):
        if v is None:
            raise ValueError("Action cannot be None")
        if not isinstance(v, str) or len(v.strip()) == 0:
            raise ValueError("Action must be a non-empty string")
        if len(v) > 50:
            raise ValueError("Action cannot exceed 50 characters")
        return v.strip()

    @field_validator('ip_address', mode='before')
    @classmethod
    def validate_ip_address(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("IP address must be a string")
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError("Invalid IP address format")
        return v

    @field_validator('changes', mode='before')
    @classmethod
    def validate_changes(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Changes must be a string")
        try:
            json.loads(v)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for changes")
        return v

    @field_validator('metadata_', mode='before')
    @classmethod
    def validate_metadata(cls, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Metadata must be a string")
        try:
            json.loads(v)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for metadata")
        return v