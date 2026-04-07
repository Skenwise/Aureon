# Middleware/DataProvider/IdentityProvider/userProvider.py
"""
User data provider.

Provides database access for SecurityUser model.
Supports deterministic retrieval, creation, update, and deletion operations.
All methods are async for FastAPI compatibility.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from database.model.security.user import SecurityUser
from backend.core.error import NotFoundError, ValidationError


class UserProvider:
    """
    Provider for user queries and operations.

    Encapsulates all database logic for users. All operations
    are deterministic and validated before returning results.

    Architecture Note:
        This provider sits between the backend adapters and the database.
        It handles ONLY database operations — no business logic.
        All methods are async to work with FastAPI's async endpoints.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the provider with an async database session.

        Args:
            session (AsyncSession): SQLAlchemy async session for DB operations.
        """
        self.session = session

    # ----------------- Create Operations ----------------- #

    async def create_user(self, user_data: dict) -> SecurityUser:
        """
        Persist a new user in the database.

        Args:
            user_data (dict): User data containing:
                - username (str): Unique username
                - email (str): Unique email address
                - hashed_password (str): Bcrypt hashed password
                - full_name (str, optional): User's full name
                - is_active (bool, optional): Whether user is active

        Returns:
            SecurityUser: The created user with ID and timestamps.

        Raises:
            ValidationError: If user with same username or email already exists.
        """
        user = SecurityUser(**user_data)
        self.session.add(user)
        
        try:
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            await self.session.rollback()
            error_msg = str(e).lower()
            if "username" in error_msg:
                raise ValidationError(f"Username '{user_data.get('username')}' already exists")
            elif "email" in error_msg:
                raise ValidationError(f"Email '{user_data.get('email')}' already exists")
            raise ValidationError(f"Failed to create user: {str(e)}")

    # ----------------- Read Operations ----------------- #

    async def get_user_by_id(self, user_id: UUID) -> Optional[SecurityUser]:
        """Retrieve a user by their unique ID."""
        return await self.session.get(SecurityUser, user_id)

    async def get_user_by_username(self, username: str) -> Optional[SecurityUser]:
        """Retrieve a user by their username."""
        stmt = select(SecurityUser).where(SecurityUser.username == username)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[SecurityUser]:
        """Retrieve a user by their email address."""
        stmt = select(SecurityUser).where(SecurityUser.email == email)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id_required(self, user_id: UUID) -> SecurityUser:
        """
        Retrieve a user by ID, raising error if not found.

        Raises:
            NotFoundError: If no user exists with the given ID.
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        return user

    async def list_users(
        self,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SecurityUser]:
        """
        List users with optional filters.

        Args:
            is_active (bool, optional): Filter by active status.
            limit (int): Maximum number of records to return.
            offset (int): Number of records to skip for pagination.
        """
        stmt = select(SecurityUser).order_by(SecurityUser.created_at.desc())  # type: ignore
        
        if is_active is not None:
            stmt = stmt.where(SecurityUser.is_active == is_active)  # type: ignore
        
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_users(self, is_active: Optional[bool] = None) -> int:
        """
        Count total users with optional filters.
        """
        stmt = select(func.count()).select_from(SecurityUser)
        
        if is_active is not None:
            stmt = stmt.where(SecurityUser.is_active == is_active)  # type: ignore
        
        result = await self.session.execute(stmt)
        return result.scalar_one()

    # ----------------- Update Operations ----------------- #

    async def update_user(self, user_id: UUID, updated_fields: dict) -> SecurityUser:
        """
        Update an existing user.

        Raises:
            NotFoundError: If user does not exist.
            ValidationError: If update would create duplicate username/email.
        """
        user = await self.get_user_by_id_required(user_id)
        
        for key, value in updated_fields.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        try:
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            await self.session.rollback()
            error_msg = str(e).lower()
            if "username" in error_msg:
                raise ValidationError(f"Username '{updated_fields.get('username')}' already taken")
            elif "email" in error_msg:
                raise ValidationError(f"Email '{updated_fields.get('email')}' already registered")
            raise ValidationError(f"Failed to update user: {str(e)}")

    async def deactivate_user(self, user_id: UUID) -> SecurityUser:
        """Deactivate a user (soft delete)."""
        return await self.update_user(user_id, {"is_active": False})

    async def activate_user(self, user_id: UUID) -> SecurityUser:
        """Activate a user."""
        return await self.update_user(user_id, {"is_active": True})

    # ----------------- Delete Operations ----------------- #

    async def delete_user(self, user_id: UUID) -> None:
        """Permanently delete a user from the database."""
        user = await self.get_user_by_id_required(user_id)
        await self.session.delete(user)
        await self.session.flush()