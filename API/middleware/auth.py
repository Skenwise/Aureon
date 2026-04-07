# API/middleware/auth.py
"""
JWT Authentication Middleware.

Validates JWT tokens on protected routes.
Extracts user and tenant context into request.state.
"""

from fastapi import Request, HTTPException, status
import jwt
import logging

from API.config import settings

logger = logging.getLogger(__name__)


class JWTAuthMiddleware:
    """
    Authentication middleware that validates JWT tokens.
    Attaches user and tenant to request.state for route handlers.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive, send=send)

        # Public routes that don't require authentication
        public_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/auth/logout",
            "/api/v1/auth/register",
        ]

        if request.url.path in public_paths:
            await self.app(scope, receive, send)
            return

        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header"
            )

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme"
                )

            # Decode and verify token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Attach user and tenant to request state
            request.state.user = {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "username": payload.get("username"),
                "tenant_id": payload.get("tenant_id"),
                "roles": payload.get("roles", [])
            }
            request.state.tenant = payload.get("tenant_id")

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Auth error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )

        await self.app(scope, receive, send)