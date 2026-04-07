# API/routes/accounts.py
"""
Chart of Accounts Routes.

Endpoints for ledger account management.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("/")
async def placeholder():
    """
    Placeholder endpoint for accounts.

    TODO: When implementing, inject Container via Depends():
    def get_accounts(container: Container = Depends(get_container)):
        return container.accounting_account.list_accounts()
    """
    return {"message": "Accounts endpoint - to be implemented"}