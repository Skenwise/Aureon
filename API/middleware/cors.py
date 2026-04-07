# API/middleware/cors.py
"""
CORS Middleware Configuration.

Sets up Cross-Origin Resource Sharing for frontend access.
"""

from fastapi.middleware.cors import CORSMiddleware

from API.config import settings


def setup_cors(app):
    """
    Configure CORS middleware for the FastAPI application.

    Args:
        app: FastAPI application instance.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )