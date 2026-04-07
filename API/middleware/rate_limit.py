# API/middleware/rate_limit.py
"""
Rate Limiting Middleware.

Limits requests per client IP to prevent abuse.
"""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from API.config import settings

# Simple in-memory rate limiter (replace with Redis in production)
rate_limit_store: Dict[str, list] = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that limits requests per client IP.
    """

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for public docs and health routes
        public_paths = ["/health", "/docs", "/redoc", "/openapi.json"]
        if request.url.path in public_paths:
            return await call_next(request)

        # Check rate limit
        current_time = time.time()
        window_start = current_time - settings.RATE_LIMIT_PERIOD_SECONDS

        # Clean old entries and get current window requests
        if client_ip not in rate_limit_store:
            rate_limit_store[client_ip] = []

        # Filter requests within current window
        rate_limit_store[client_ip] = [
            timestamp for timestamp in rate_limit_store[client_ip]
            if timestamp > window_start
        ]

        # Check limit
        if len(rate_limit_store[client_ip]) >= settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Max {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_PERIOD_SECONDS} seconds."
            )

        # Add current request
        rate_limit_store[client_ip].append(current_time)

        return await call_next(request)