# models/security/permission.py

"""
Security permission models.

Defines atomic permission entities and immutable Role→Permission assignments
used for internal authorization. Permissions are granular actions that
roles can perform in the system.
"""

from uuid import UUID, uuid4
from typing import Optional
from sqlmodel import Field, ForeignKey
from ..base import BaseModel


class SecurityPermission(BaseModel, table=True):
    """
    Atomic permission entity.

    Represents a single permission code that can be granted to roles.
    """
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique identifier for the permission",
    )

    code: str = Field(
        unique=True,
        index=True,
        nullable=False,
        description="Machine-readable permission code (e.g., 'ledger.view')",
    )

    description: Optional[str] = Field(
        default=None,
        description="Semantic description of what the permission allows",
    )


class RolePermission(BaseModel, table=True):
    """
    Immutable assignment linking a Role to a Permission.

    Represents many-to-many relationship: Roles ←→ Permissions.
    """
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique identifier for the role-permission mapping",
    )

    role_id: UUID = Field(
        foreign_key="securityrole.id",
        nullable=False,
        index=True,
        description="ID of the role granting the permission",
    )

    permission_id: UUID = Field(
        foreign_key="securitypermission.id",
        nullable=False,
        index=True,
        description="ID of the granted permission",
    )
