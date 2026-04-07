"""
Permission data provider.
Provides database access for SecurityPermission and RolePermissionLink models.
"""
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.model.security.permission import SecurityPermission
from database.model.security.role import RolePermissionLink
from database.model.security.user import SecurityUser
from backend.core.error import NotFoundError


class SecurityPermissionProvider:
    """
    Provider for permission and role-permission queries.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the provider with a database session.
        """
        self.session = session
    
    async def get_permission_by_name(self, name: str) -> SecurityPermission:
        """
        Retrieve a permission by its name.
        
        Args:
            name (str): Permission name (e.g., "loan.create").
        
        Returns:
            SecurityPermission: Permission object if found.
        
        Raises:
            NotFoundError: If no permission with the given name exists.
        """
        stmt = select(SecurityPermission).where(SecurityPermission.name == name)  # type: ignore
        result = await self.session.execute(stmt)
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise NotFoundError("Permission", name)
        
        return permission
    
    async def get_permission_by_resource_action(self, resource: str, action: str) -> SecurityPermission:
        """
        Retrieve a permission by resource and action.
        
        Args:
            resource (str): Resource name (e.g., "loan").
            action (str): Action name (e.g., "create").
        
        Returns:
            SecurityPermission: Permission object if found.
        
        Raises:
            NotFoundError: If no permission exists.
        """
        stmt = select(SecurityPermission).where(
            SecurityPermission.resource == resource,  # type: ignore
            SecurityPermission.action == action  # type: ignore
        )
        result = await self.session.execute(stmt)
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise NotFoundError("Permission", f"{resource}.{action}")
        
        return permission
    
    async def list_permissions(self) -> List[SecurityPermission]:
        """
        List all permissions in the system.
        
        Returns:
            List[SecurityPermission]: All available permissions.
        """
        stmt = select(SecurityPermission)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_permissions_for_role(self, role_id: UUID) -> List[SecurityPermission]:
        """
        Retrieve all permissions granted to a specific role.
        
        Args:
            role_id (UUID): Role ID to lookup.
        
        Returns:
            List[SecurityPermission]: List of permissions associated with the role.
        """
        stmt = (
            select(SecurityPermission)
            .join(RolePermissionLink, SecurityPermission.id == RolePermissionLink.permission_id) # type: ignore
            .where(RolePermissionLink.role_id == role_id)
        )
        
        result = await self.session.execute(stmt)
        permissions = list(result.scalars().all())
        return permissions
    
    async def get_roles_with_permission(self, permission_name: str) -> List[UUID]:
        """
        Retrieve role IDs that include a specific permission.
        
        Args:
            permission_name (str): Permission name to filter by.
        
        Returns:
            List[UUID]: List of role IDs granting this permission.
        """
        permission = await self.get_permission_by_name(permission_name)
        
        stmt = select(RolePermissionLink.role_id).where(
            RolePermissionLink.permission_id == permission.id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def user_has_permission(self, user_id: UUID, permission_name: str) -> bool:
        """
        Check if the user has a specific permission via their assigned role.

        Args:
            user_id (UUID): ID of the user.
            permission_name (str): Permission name to check.

        Returns:
            bool: True if the user has the permission, False otherwise.
        """
        # 1. Get the user's role_id
        stmt_user = select(SecurityUser.role_id).where(SecurityUser.id == user_id)  # type: ignore
        result_user = await self.session.execute(stmt_user)
        role_id = result_user.scalar()

        if not role_id:
            return False  # user has no role assigned

        # 2. Get the permission object
        try:
            permission = await self.get_permission_by_name(permission_name)
        except NotFoundError:
            return False

        # 3. Check if the role grants this permission
        stmt_check = (
            select(RolePermissionLink.role_id)
            .where(RolePermissionLink.role_id == role_id)
            .where(RolePermissionLink.permission_id == permission.id)
        )
        result_check = await self.session.execute(stmt_check)
        return bool(result_check.scalar())
