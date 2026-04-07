# API/routes/auth.py
"""
Authentication Routes.

Public endpoints for user registration, login, and token management.

IMPORTANT: These endpoints do NOT use the standard Container dependency
because the user is not authenticated yet. They manually instantiate
providers and adapters with a database session.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime
import bcrypt
import os

from database.sessionmaker import get_async_db_session as get_db
from backend.core.error import AuthenticationError
from backend.identity.auth import AuthenticationAdapter
from Middleware.DataProvider.IdentityProvider.userProvider import UserProvider


router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============================================================================
# API SCHEMAS
# ============================================================================

class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., description="User's username", min_length=3, max_length=50)
    password: str = Field(..., description="User's password", min_length=1)


class RegisterRequest(BaseModel):
    """
    Registration request schema.
    
    DEV ONLY: In production, user creation is restricted to Admins after KYC verification.
    """
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=900, description="Token expiration in seconds (15 minutes)")


class RegisterResponse(BaseModel):
    """Registration response schema."""
    id: UUID
    username: str
    email: EmailStr
    full_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    
    DEV ONLY: This endpoint is for development and testing.
    In production, user creation requires admin privileges and KYC verification.
    """
    try:
        # Initialize provider with async session
        user_provider = UserProvider(db)
        
        # Check if username already exists
        existing_user = await user_provider.get_user_by_username(request.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{request.username}' is already taken"
            )
        
        # Check if email already exists
        existing_email = await user_provider.get_user_by_email(request.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{request.email}' is already registered"
            )
        
        # Hash the password
        hashed_password = bcrypt.hashpw(
            request.password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")
        
        # Create user data dict
        user_data = {
            "username": request.username,
            "email": request.email,
            "hashed_password": hashed_password,
            "full_name": request.full_name,
            "is_active": True
        }
        
        # Create user via provider
        new_user = await user_provider.create_user(user_data)
        
        # Return user info (password excluded)
        return RegisterResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate a user and return a JWT access token.
    
    This endpoint does NOT use the standard Container dependency because
    authentication is required to GET the Container.
    """
    # Ensure JWT_SECRET is set
    if not os.environ.get("JWT_SECRET"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET environment variable not set"
        )
    
    try:
        # Manual instantiation (bypasses Container)
        user_provider = UserProvider(db)
        auth_adapter = AuthenticationAdapter(provider=user_provider)
        
        token = await auth_adapter.authenticate(
            username=request.username,
            password=request.password
        )
        
        return TokenResponse(access_token=token)
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.post("/refresh")
async def refresh_token():
    """
    Refresh access token using refresh token.
    
    TODO: Implement refresh token logic
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token not implemented yet"
    )


@router.post("/logout")
async def logout():
    """
    Logout current user.
    
    Note: JWT is stateless, so logout is handled client-side
    by discarding the token. This endpoint exists for completeness.
    """
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_current_user():
    """
    Get current authenticated user.
    
    TODO: Implement with authenticated container
    """
    return {
        "message": "This endpoint requires authentication via JWT token",
        "implementation_status": "pending - requires authenticated container"
    }