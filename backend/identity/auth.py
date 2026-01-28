# backend/identity/auth.py

"""
Identity authentication port and adapter.

Defines the contract for authenticating users and verifying authentication tokens.
This module isolates authentication logic from infrastructure details.
"""

from typing import Protocol, Dict
from Middleware.DataProvider.IdentityProvider.userProvider import UserProvider
from backend.core.error import AuthenticationError
import bcrypt
import jwt
from datetime import datetime, timedelta
import os


class AuthenticationPort(Protocol):
    """
    Port interface for authentication operations.

    This interface defines how the identity module authenticates users
    and validates authentication tokens, without exposing implementation
    details such as hashing algorithms or token mechanisms.
    """

    def authenticate(self, username: str, password: str) -> str:
        """
        Authenticate a user using credentials.

        Args:
            username (str): User's unique username.
            password (str): Plain-text password provided by the user.

        Returns:
            str: An authentication token representing the authenticated user.

        Raises:
            AuthenticationError: If authentication fails.
        """
        raise NotImplementedError

    def verify_token(self, token: str) -> Dict[str, str]:
        """
        Verify an authentication token.

        Args:
            token (str): Authentication token.

        Returns:
            Dict[str, str]: Decoded token payload containing identity claims.

        Raises:
            AuthenticationError: If token is invalid or expired.
        """
        raise NotImplementedError


class AuthenticationAdapter(AuthenticationPort):
    """
    Adapter implementing the AuthenticationPort.

    Translates authentication operations into concrete implementations
    using password hashing (bcrypt) and token generation (JWT).
    """

    def __init__(
        self,
        provider: UserProvider,
        secret_key: str | None = None,
        token_expiry_hours: int = 24,
    ):
        """
        Initialize the adapter with a user provider and security configuration.

        Args:
            provider (UserProvider): The database provider for user operations.
            secret_key (str | None): Secret key for JWT token signing.
                If None, the value is loaded from the environment.
            token_expiry_hours (int): Token validity duration in hours (default: 24).

        Teaching Point:
        - The adapter depends on UserProvider (already established pattern)
        - Secret key should come from environment variables in production
        - Token expiry is configurable for flexibility
        """
        self.provider = provider
        self.secret_key = secret_key or os.environ["JWT_SECRET"]
        self.token_expiry_hours = token_expiry_hours
        self.algorithm = "HS256"

    def authenticate(self, username: str, password: str) -> str:
        """
        Authenticate a user and return a JWT token.

        Process:
        1. Retrieve user from provider by username
        2. Verify password against stored hash
        3. Generate JWT token with user claims

        Args:
            username (str): User's unique username.
            password (str): Plain-text password.

        Returns:
            str: JWT authentication token.

        Raises:
            AuthenticationError: If user not found or password incorrect.

        Teaching Point:
        - We fetch the user first, then verify the password
        - Password verification uses bcrypt (constant-time comparison)
        - Token generation includes user_id and username as claims
        """
        user = self.provider.get_user_by_username(username)

        if not user:
            raise AuthenticationError("Invalid username or password")

        if not self._verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid username or password")

        token = self._generate_token(str(user.id), user.username)
        return token

    def verify_token(self, token: str) -> Dict[str, str]:
        """
        Verify and decode a JWT token.

        Process:
        1. Decode the JWT using the secret key
        2. Verify signature and expiration
        3. Return payload containing identity claims

        Args:
            token (str): JWT token to verify.

        Returns:
            Dict[str, str]: Decoded payload with user_id and username.

        Raises:
            AuthenticationError: If token is invalid, expired, or malformed.

        Teaching Point:
        - JWT verification checks both signature and expiration automatically
        - We catch specific JWT exceptions and translate to domain errors
        - This prevents infrastructure errors from leaking to the API layer
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")

        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")

    # --- Private Helper Methods ---
    # These are implementation details, not part of the Port contract

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a plain-text password against a bcrypt hash.

        Args:
            password (str): Plain-text password.
            password_hash (str): Stored bcrypt hash.

        Returns:
            bool: True if password matches, False otherwise.

        Teaching Point:
        - bcrypt.checkpw performs constant-time comparison
        - This prevents timing attacks where attackers measure response time
        - Static method because it doesn't need instance state
        """
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                password_hash.encode("utf-8"),
            )
        except Exception:
            # If hash is malformed or any error occurs, fail safely
            return False

    def _generate_token(self, user_id: str, username: str) -> str:
        """
        Generate a JWT token with user claims.

        Args:
            user_id (str): User's unique identifier.
            username (str): User's username.

        Returns:
            str: Encoded JWT token.

        Teaching Point:
        - JWT payload contains three timestamps:
          * iat (issued at): when token was created
          * exp (expiration): when token becomes invalid
        - We include minimal user info (id, username)
        - Never include sensitive data like passwords in JWT
        """
        now = datetime.utcnow()
        expiry = now + timedelta(hours=self.token_expiry_hours)

        payload = {
            "user_id": user_id,
            "username": username,
            "iat": int(now.timestamp()),
            "exp": int(expiry.timestamp()),
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
