# backend/identity/user.py
from typing import Optional
from schemas.userSchema import UserCreate, UserUpdate, UserRead
from typing import Protocol
from Middleware.DataProvider.IdentityProvider.userProvider import UserProvider
from backend.core.error import NotFoundError


class UserManagementPort(Protocol):
    """
    Port interface for user management operations.
    Defines the contract between the Identity service layer
    and the underlying data provider or adapter.

    This ensures the service layer can manage users without
    knowing database details.
    """

    def create_user(self, user_data: UserCreate) -> UserRead:
        """
        Create a new user.

        Args:
            user_data (UserCreate): Data required to create a user.

        Returns:
            UserRead: The created user.

        Raises:
            ValidationError: If creation fails due to validation rules.
        """
        raise NotImplementedError

    def get_user_by_id(self, user_id: str) -> UserRead:
        """
        Retrieve a user by their unique ID.

        Args:
            user_id (str): The ID of the user.

        Returns:
            UserRead: The user if found.

        Raises:
            NotFoundError: If the user does not exist.
        """
        raise NotImplementedError

    def get_user_by_username(self, username: str) -> UserRead:
        """
        Retrieve a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            UserRead: The user if found.

        Raises:
            NotFoundError: If the user does not exist.
        """
        raise NotImplementedError

    def update_user(self, user_id: str, update_data: UserUpdate) -> UserRead:
        """
        Update an existing user's data.

        Args:
            user_id (str): The ID of the user to update.
            update_data (UserUpdate): Fields to update.

        Returns:
            UserRead: The updated user.

        Raises:
            NotFoundError: If the user does not exist.
        """
        raise NotImplementedError

    def delete_user(self, user_id: str) -> None:
        """
        Delete a user by their unique ID.

        Args:
            user_id (str): The ID of the user to delete.

        Returns:
            None

        Raises:
            NotFoundError: If the user does not exist.
        """
        raise NotImplementedError


class UserManagementAdapter(UserManagementPort):
    """
    Adapter implementing the UserManagementPort.
    Translates service layer calls into provider operations.
    """

    def __init__(self, provider: UserProvider):
        """
        Initialize the adapter with a provider.

        Args:
            provider (UserProvider): The database provider for user operations.
        """
        self.provider = provider

    def create_user(self, user_data: UserCreate) -> UserRead:
        user = self.provider.create_user(user_data)
        return UserRead.model_validate(user)

    def get_user_by_id(self, user_id: str) -> UserRead:
        user = self.provider.get_user_by_id(user_id)
        return UserRead.model_validate(user)

    def get_user_by_username(self, username: str) -> UserRead:
        user = self.provider.get_user_by_username(username)
        return UserRead.model_validate(user)

    def update_user(self, user_id: str, update_data: UserUpdate) -> UserRead:
        user = self.provider.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        updated_user = self.provider.update_user(user, update_data)
        return UserRead.model_validate(updated_user)

    def delete_user(self, user_id: str) -> None:
        user = self.provider.get_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        self.provider.delete_user(user)
