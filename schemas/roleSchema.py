# schemas/roleSchema.py

"""
Role schemas.

Defines immutable role representations used by the Identity module.
Roles represent structural authority and are read-only by design.
"""

from typing import List
from pydantic import BaseModel, Field


class RoleRead(BaseModel):
    """
    Read-only representation of a role.

    Roles are immutable authority constructs.
    They define what actions are structurally allowed,
    not temporary privileges.
    """

    id: str = Field(..., description="Unique identifier of the role")
    name: str = Field(..., description="Unique, human-readable role name")
    description: str = Field(..., description="Semantic meaning of the role")
    permissions: List[str] = Field(
        default_factory=list,
        description="Permission codes associated with the role"
    )

    model_config = {
        "from_attributes": True
    }
