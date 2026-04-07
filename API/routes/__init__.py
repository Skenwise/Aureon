# API/routes/__init__.py
"""
API Routes.

Exports all route routers for the FastAPI application.
"""

from .auth import router as auth_router
from .users import router as users_router
from .tenants import router as tenants_router
from .accounts import router as accounts_router
from .journals import router as journals_router
from .loans import router as loans_router
from .payments import router as payments_router
from .treasury import router as treasury_router
from .reports import router as reports_router
from .audit import router as audit_router
from .currency import router as currency_router
from .health import router as health_router

__all__ = [
    "auth_router",
    "users_router",
    "tenants_router",
    "accounts_router",
    "journals_router",
    "loans_router",
    "payments_router",
    "treasury_router",
    "reports_router",
    "audit_router",
    "currency_router",
    "health_router",
]