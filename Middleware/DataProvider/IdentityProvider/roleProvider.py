"""
Role data provider.
Provides database access for SecurityRole model.
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.model.security.role import SecurityRole
from backend.core.error import NotFoundError


class SecurityRoleProvider:
    """
    Provider for role queries and operations.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the provider with a database session.
        """
        self.session = session
    
    async def create_role(self, role: SecurityRole) -> SecurityRole:
        """
        Create a new role.
        """
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role
    
    async def get_role(self, role_id: UUID) -> SecurityRole:
        """
        Retrieve a role by its unique ID.
        """
        role = await self.session.get(SecurityRole, role_id)
        if not role:
            raise NotFoundError("Role", str(role_id))
        return role
    
    async def get_role_by_name(self, name: str) -> Optional[SecurityRole]:
        """
        Retrieve a role by its name.
        """
        stmt = select(SecurityRole).where(SecurityRole.name == name)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_roles(self) -> List[SecurityRole]:
        """
        List all roles.
        """
        stmt = select(SecurityRole)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_role(self, role_id: UUID, updated_fields: dict) -> SecurityRole:
        """
        Update an existing role.
        """
        role = await self.get_role(role_id)
        for key, value in updated_fields.items():
            if hasattr(role, key):
                setattr(role, key, value)
        self.session.add(role)
        await self.session.commit()
        await self.session.refresh(role)
        return role
    
    async def delete_role(self, role_id: UUID) -> None:
        """
        Delete a role.
        """
        role = await self.get_role(role_id)
        await self.session.delete(role)
        await self.session.commit()
