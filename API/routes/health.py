# API/routes/health.py
"""
Health Check Routes.

Simple endpoints for monitoring and readiness checks.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/load balancers."""
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes."""
    return {"status": "alive"}