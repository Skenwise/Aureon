# models/security/user.py
from sqlmodel import Field
from uuid import UUID
from typing import Optional
from datetime import datetime
from ..base import BaseModel

class SecurityUser(BaseModel, table=True):
    """
    Internal system user (ops, admin, auditor).
    NEVER customers.
    """
    email: str = Field(index=True, unique=True)
    username: str = Field(index=True, unique=True)

    hashed_password: str

    is_active: bool = Field(default=True, index=True)
    is_superuser: bool = Field(default=False)

    role_id: Optional[UUID] = Field(default=None)

    last_login_at: Optional[datetime] = None