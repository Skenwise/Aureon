# database/model/security/role.py
from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from pydantic import field_validator

from database.model.base import BaseModel

if TYPE_CHECKING:
    from database.model.core.user import User  # Only import core User


class RolePermissionLink(SQLModel, table=True):
    """
    Association table between roles and permissions.
    """
    
    role_id: UUID = Field(foreign_key="securityrole.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="securitypermission.id", primary_key=True)


class SecurityRole(BaseModel, table=True):
    """
    Role model for RBAC.
    """
    
    name: str = Field(..., max_length=50, unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=255)
    is_default: bool = Field(default=False)
    
    # Relationships - uses core User model
    users: List["User"] = Relationship(back_populates="role")
    
    @field_validator('name', mode='before')
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Role name cannot be empty")
        return v.strip()