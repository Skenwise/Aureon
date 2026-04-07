"""
API Configuration.

Loads environment variables and provides settings for the API layer.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    API settings loaded from environment variables.
    Values can be overridden by .env file or system environment.
    """

    # ============================================================================
    # API Basic Configuration
    # ============================================================================
    API_V1_PREFIX: str = Field(default="/api/v1", description="API version prefix")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # ============================================================================
    # Security - JWT Authentication
    # ============================================================================
    JWT_SECRET_KEY: str = Field(
        default="your-super-secret-key-change-in-production",
        description="Secret key for JWT signing (change in production!)"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15,
        description="Access token validity in minutes"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token validity in days"
    )

    # ============================================================================
    # CORS - Cross-Origin Resource Sharing
    # ============================================================================
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed frontend origins"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hostnames"
    )

    # ============================================================================
    # Rate Limiting
    # ============================================================================
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Max requests per period")
    RATE_LIMIT_PERIOD_SECONDS: int = Field(default=60, description="Rate limit period in seconds")

    # ============================================================================
    # Logging
    # ============================================================================
    LOG_LEVEL: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or text)")

    # ============================================================================
    # Database
    # ============================================================================
    DATABASE_URL: str = Field(
        default="postgresql://postgres:Black99raiser%*@localhost:5432/loansystem",
        description="PostgreSQL database connection URL"
    )

    # ============================================================================
    # Redis (for rate limiting and caching - optional)
    # ============================================================================
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for rate limiting and caching"
    )
    REDIS_ENABLED: bool = Field(default=False, description="Enable Redis for rate limiting")

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create a single instance to be imported everywhere
settings = Settings()
