# database/model/core/user.py
from sqlmodel import Field, Relationship
from uuid import UUID
from typing import Optional, TYPE_CHECKING, List

from database.model.base import BaseModel

if TYPE_CHECKING:
    from database.model.security.role import SecurityRole
    from database.model.core.company import Company
    from database.model.finance.journal import Journal


class User(BaseModel, table=True):
    
    username: str = Field(..., unique=True, max_length=50)
    email: str = Field(..., unique=True, max_length=150)
    hashed_password: str = Field(..., max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)
    
    # Foreign key to role table
    role_id: Optional[UUID] = Field(default=None, foreign_key="securityrole.id")
    
    # Relationships
    role: Optional["SecurityRole"] = Relationship(back_populates="users")
    company: Optional["Company"] = Relationship(back_populates="users")
    journals_created: List["Journal"] = Relationship(back_populates="creator")