# API/routes/reports.py
"""
Financial Reports Routes.

Endpoints for balance sheet, income statement, trial balance, and portfolio reports.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/")
async def placeholder():
    """
    Placeholder endpoint for reports.

    TODO: When implementing, inject Container via Depends():
    def get_balance_sheet(container: Container = Depends(get_container)):
        return container.reporting_ledger.get_balance_sheet(...)
    """
    return {"message": "Reports endpoint - to be implemented"}