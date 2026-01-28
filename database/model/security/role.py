# models/security/role.py

"""
Security role model.

Defines immutable system roles used for internal authorization.
Roles represent structural authority and are not meant to change
frequently or dynamically at runtime.
"""

from typing import List
from uuid import UUID, uuid4

from sqlmodel import Field, Column, JSON
from ..base import BaseModel


class SecurityRole(BaseModel, table=True):
    """
    Immutable security role.

    A role defines a stable set of permissions that can be assigned
    to internal system users (ops, admin, auditor).
    """

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        description="Unique identifier for the role",
    )

    name: str = Field(
        unique=True,
        index=True,
        nullable=False,
        description="Unique, human-readable role name",
    )

    description: str = Field(
        nullable=False,
        description="Semantic description of the role's authority",
    )

    permissions: List[str] = Field(
        sa_column_kwargs={"type_": JSON},
        default_factory=list,
        nullable=False,
        description="List of permission codes granted by this role",
    )
