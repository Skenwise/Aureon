# API/routes/currency.py
"""
Currency Management Routes.

Endpoints for currency and exchange rate operations.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/currency", tags=["Currency"])


@router.get("/")
async def placeholder():
    """
    Placeholder endpoint for currency.

    TODO: When implementing, inject Container via Depends():
    def get_currencies(container: Container = Depends(get_container)):
        return container.currency.list_currencies()
    """
    return {"message": "Currency endpoint - to be implemented"}