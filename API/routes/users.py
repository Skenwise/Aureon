# API/routes/users.py
"""
User Management Routes.

Endpoints for creating, retrieving, updating, and deleting users.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def placeholder():
    """
    Placeholder endpoint for users.

    TODO: When implementing, inject Container via Depends():
    def get_users(container: Container = Depends(get_container)):
        return container.user.list_users()
    """
    return {"message": "Users endpoint - to be implemented"}