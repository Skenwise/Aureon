# Middleware/DataProvider/Identityrovider/userProvider.py
from typing import Optional
from sqlmodel import Session, select
from database.model.core.user import User
from schemas.userSchema import UserCreate, UserUpdate
from backend.core.error import NotFoundError

class UserProvider:
    """
    Data provider for User operations.
    Handles all direct interactions with the database for User entities.

    This class isolates database operations, so service layers or adapters
    do not need to know about SQLModel or DB session management.
    """

    def __init__(self, session: Session):
        """
        Initialize the provider with a database session.

        Args:
            session (Session): SQLModel session for database operations.
        """
        self.session = session

    def create_user(self, user_data: UserCreate) -> User:
        """
        Insert a new user into the database.

        Args:
            user_data (UserCreate): Data for the new user.

        Returns:
            User: The created user ORM object.
        """
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=user_data.password,  # hash in service layer if needed
            full_name=user_data.full_name
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a user by their ID.

        Args:
            user_id (str): User's unique ID.

        Returns:
            Optional[User]: User if found, else None.
        """
        statement = select(User).where(User.id == user_id)
        result = self.session.exec(statement).first()
        if not result:
            raise NotFoundError("User", user_id)
        return result

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by their username.

        Args:
            username (str): User's unique username.

        Returns:
            Optional[User]: User if found, else None.
        """
        statement = select(User).where(User.username == username)
        result = self.session.exec(statement).first()
        if not result:
            raise NotFoundError("User", username)
        return result

    def update_user(self, user: User, update_data: UserUpdate) -> User:
        """
        Update user fields in the database.

        Args:
            user (User): The existing user ORM object.
            update_data (UserUpdate): Fields to update.

        Returns:
            User: Updated user ORM object.
        """
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete_user(self, user: User) -> None:
        """
        Delete a user from the database.

        Args:
            user (User): The user ORM object to delete.

        Returns:
            None
        """
        self.session.delete(user)
        self.session.commit()
