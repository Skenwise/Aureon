# schemas/permissionSchema.py

"""
Permission schemas.

Defines read-only permission representations used by the
Identity and Authorization layers.
"""

from pydantic import BaseModel, ConfigDict
from typing import List


class PermissionCheck(BaseModel):
    """
    Permission check request.

    Represents an authorization question:
    does a given user have a specific permission?
    """

    user_id: str
    permission: str

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class PermissionRead(BaseModel):
    """
    Permission representation.

    Used for introspection, debugging, or audit views.
    """

    code: str
    description: str

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )
