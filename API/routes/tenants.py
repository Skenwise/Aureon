# API/routes/tenants.py
"""
Tenant Management Routes.

Endpoints for multi-tenant institution management.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.get("/")
async def placeholder():
    """
    Placeholder endpoint for tenants.

    TODO: When implementing, inject Container via Depends():
    def get_tenants(container: Container = Depends(get_container)):
        return container.tenant_provider.list_tenants()
    """
    return {"message": "Tenants endpoint - to be implemented"}