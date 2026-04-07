# API/routes/journals.py
"""
Journal Entry Routes.

Endpoints for creating, posting, and reversing journal entries.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/journals", tags=["Journals"])


@router.get("/")
async def placeholder():
    """
    Placeholder endpoint for journals.

    TODO: When implementing, inject Container via Depends():
    def get_journals(container: Container = Depends(get_container)):
        return container.accounting_journal.list_journals()
    """
    return {"message": "Journals endpoint - to be implemented"}