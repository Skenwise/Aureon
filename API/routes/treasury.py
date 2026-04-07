# API/routes/treasury.py
"""
Treasury Routes.

Endpoints for liquidity, cash positions, and fund transfers.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/treasury", tags=["Treasury"])


@router.get("/")
async def placeholder():
    """
    Placeholder endpoint for treasury.

    TODO: When implementing, inject Container via Depends():
    def get_liquidity(container: Container = Depends(get_container)):
        return container.liquidity.get_total_liquidity()
    """
    return {"message": "Treasury endpoint - to be implemented"}