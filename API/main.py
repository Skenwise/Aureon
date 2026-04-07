# API/main.py
"""
Aureon API Entry Point.

FastAPI application with all routes and middleware.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from API.config import settings
from API.middleware import JWTAuthMiddleware, LoggingMiddleware, RateLimitMiddleware, setup_cors
from API.routes import (
    auth, users, tenants, accounts, journals,
    loans, payments, treasury, reports, audit, currency, health
)

# Create FastAPI application
app = FastAPI(
    title="Aureon API",
    description="Core Banking & Loan Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS first
setup_cors(app)

# Logging
app.add_middleware(LoggingMiddleware)

# Rate Limiting
app.add_middleware(RateLimitMiddleware)

# Authentication (must be last)
app.add_middleware(JWTAuthMiddleware)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent response format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.__class__.__name__,
                "message": exc.detail,
                "request_id": request.headers.get("X-Request-ID")
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Handle request validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": errors,
                "request_id": request.headers.get("X-Request-ID")
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request.headers.get("X-Request-ID")
            }
        }
    )


# ============================================================================
# ROUTES
# ============================================================================

# Health check
app.include_router(health.router)

# Authentication
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

# Users & Tenants
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(tenants.router, prefix=settings.API_V1_PREFIX)

# Accounting
app.include_router(accounts.router, prefix=settings.API_V1_PREFIX)
app.include_router(journals.router, prefix=settings.API_V1_PREFIX)

# Loans
app.include_router(loans.router, prefix=settings.API_V1_PREFIX)

# Payments
app.include_router(payments.router, prefix=settings.API_V1_PREFIX)

# Treasury
app.include_router(treasury.router, prefix=settings.API_V1_PREFIX)

# Reporting
app.include_router(reports.router, prefix=settings.API_V1_PREFIX)

# Audit
app.include_router(audit.router, prefix=settings.API_V1_PREFIX)

# Currency
app.include_router(currency.router, prefix=settings.API_V1_PREFIX)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Aureon API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": "1.0.0"}