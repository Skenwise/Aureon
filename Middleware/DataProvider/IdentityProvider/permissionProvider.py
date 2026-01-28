# Middleware/DataProvider/IdentityProvider/permissionProvider.py
"""
Permission data provider.
Provides database access for SecurityPermission and RolePermission models.
Supports read-only operations for immutable roles and permissions.
"""
from typing import List
from uuid import UUID
from sqlmodel import select, Session
from database.model.security.permission import SecurityPermission, RolePermission
from backend.core.error import NotFoundError
from database.model.security.user import SecurityUser


class SecurityPermissionProvider:
    """
    Provider for permission and role-permission queries.
    Encapsulates all database logic for retrieving permissions
    and role-to-permission mappings.
    """
    
    def __init__(self, session: Session):
        """
        Initialize the provider with a database session.
        
        Args:
            session (Session): SQLModel session for DB operations.
        """
        self.session = session
    
    def get_permission_by_code(self, code: str) -> SecurityPermission:
        """
        Retrieve a permission by its code.
        
        Args:
            code (str): Unique machine-readable permission code.
        
        Returns:
            SecurityPermission: Permission object if found.
        
        Raises:
            NotFoundError: If no permission with the given code exists.
        """
        stmt = select(SecurityPermission).where(SecurityPermission.code == code)
        permission = self.session.exec(stmt).first()
        
        if not permission:
            raise NotFoundError("Permission", code)
        
        return permission
    
    def list_permissions(self) -> List[SecurityPermission]:
        """
        List all permissions in the system.
        
        Returns:
            List[SecurityPermission]: All available permissions.
        """
        stmt = select(SecurityPermission)
        return list(self.session.exec(stmt).all())
    
    def get_permissions_for_role(self, role_id: UUID) -> List[SecurityPermission]:
        """
        Retrieve all permissions granted to a specific role.
        
        Args:
            role_id (UUID): Role ID to lookup.
        
        Returns:
            List[SecurityPermission]: List of permissions associated with the role.
        """
        stmt = (
            select(SecurityPermission)
            .join(RolePermission).where(SecurityPermission.id == RolePermission.permission_id)
            .where(RolePermission.role_id == role_id)
        )
        
        permissions = list(self.session.exec(stmt).all())
        return permissions
    
    def get_roles_with_permission(self, permission_code: str) -> List[UUID]:
        """
        Retrieve role IDs that include a specific permission.
        
        Args:
            permission_code (str): Permission code to filter by.
        
        Returns:
            List[UUID]: List of role IDs granting this permission.
        """
        permission = self.get_permission_by_code(permission_code)
        
        stmt = select(RolePermission.role_id).where(
            RolePermission.permission_id == permission.id
        )
        
        return list(self.session.exec(stmt).all())
    

    def user_has_permission(self, user_id: UUID, permission_code: str) -> bool:
        """
        Check if the user has a specific permission via their assigned role.

        Args:
            user_id (UUID): ID of the user.
            permission_code (str): Permission code to check.

        Returns:
            bool: True if the user has the permission, False otherwise.
        """
        # 1. Get the user's role_id
        stmt_user = select(SecurityUser.role_id).where(SecurityUser.id == user_id)
        role_id = self.session.exec(stmt_user).first()

        if not role_id:
            return False  # user has no role assigned

        # 2. Get the permission object
        try:
            permission = self.get_permission_by_code(permission_code)
        except NotFoundError:
            return False

        # 3. Check if the role grants this permission
        stmt_check = (
            select(RolePermission.role_id)
            .where(RolePermission.role_id == role_id)
            .where(RolePermission.permission_id == permission.id)
        )
        return bool(self.session.exec(stmt_check).first())
