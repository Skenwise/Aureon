# database/model/security/permission.py
from sqlmodel import Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from database.model.base import BaseModel

if TYPE_CHECKING:
    from .role import SecurityRole


class SecurityPermission(BaseModel, table=True):
    """
    Permission model for RBAC.
    """
    
    name: str = Field(..., max_length=100, unique=True, index=True)
    resource: str = Field(..., max_length=50)
    action: str = Field(..., max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    
    # TODO: Fix relationship later
    # roles: List["SecurityRole"] = Relationship(back_populates="permissions")