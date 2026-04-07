# API/routes/loans.py
"""
Loan Routes.

Endpoints for loan lifecycle management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from uuid import UUID

from API.dependencies import get_container, Container
from schemas.loanSchema import LoanCreate, LoanRead, LoanUpdate
from backend.core.error import NotFoundError, ValidationError

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post("/", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
async def create_loan(
    request: LoanCreate,
    container: Container = Depends(get_container)
):
    """
    Create a new loan application.
    """
    try:
        loan = container.loans.create_loan(request)
        return loan
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{loan_id}", response_model=LoanRead)
async def get_loan(
    loan_id: UUID,
    container: Container = Depends(get_container)
):
    """
    Get loan by ID.
    """
    try:
        loan = container.loans.get_loan(loan_id)
        return loan
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/", response_model=List[LoanRead])
async def list_loans(
    borrower_id: Optional[UUID] = None,
    status: Optional[str] = None,
    container: Container = Depends(get_container)
):
    """
    List all loans with optional filters.
    """
    loans = container.loans.list_loans(borrower_id, status)
    return loans


@router.patch("/{loan_id}/status", response_model=LoanRead)
async def update_loan_status(
    loan_id: UUID,
    new_status: str,  # Changed from 'status' to avoid conflict with imported status
    container: Container = Depends(get_container)
):
    """
    Update loan status.
    """
    try:
        loan = container.loans.update_loan_status(loan_id, new_status)
        return loan
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )