# API/routes/payments.py
"""
Payment Routes.

Endpoints for outbound, inbound, and settlement payment operations.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/")
async def placeholder():
    """
    Placeholder endpoint for payments.

    TODO: When implementing, inject Container via Depends():
    def get_payments(container: Container = Depends(get_container)):
        return container.payments_outbound.list_outbound_payments()
    """
    return {"message": "Payments endpoint - to be implemented"}