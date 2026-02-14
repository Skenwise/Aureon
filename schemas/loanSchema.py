# schemas/loanSchema.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID


# ==================== LOAN SCHEMAS ====================

class LoanCreate(BaseModel):
    """
    Schema for creating a new loan.
    Validates input data before passing to the service layer.
    """
    borrower_id: UUID = Field(..., description="Customer ID of the borrower")
    principal_amount: Decimal = Field(..., gt=0, description="Loan principal amount (must be positive)")
    interest_rate: Decimal = Field(..., ge=0, le=100, description="Annual interest rate (0-100%)")
    term_months: int = Field(..., gt=0, description="Loan term in months")
    currency_code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    start_date: date = Field(..., description="Loan start date")
    product_type: str = Field(..., max_length=50, description="Loan product type (e.g., 'PERSONAL', 'BUSINESS')")
    disbursement_account_id: UUID = Field(..., description="Account to disburse funds to")
    repayment_frequency: Literal["MONTHLY", "WEEKLY", "BIWEEKLY"] = Field(default="MONTHLY", description="Repayment frequency")
    notes: Optional[str] = Field(None, max_length=500, description="Additional loan notes")
    
    @field_validator('principal_amount')
    def validate_principal(cls, v):
        if v <= 0:
            raise ValueError("Principal amount must be positive")
        return v


class LoanUpdate(BaseModel):
    """
    Schema for updating an existing loan.
    Only status transitions are typically allowed after creation.
    """
    status: Optional[Literal["PENDING", "DISBURSED", "ACTIVE", "CLOSED", "DEFAULTED"]] = Field(
        None, description="Updated loan status"
    )
    notes: Optional[str] = Field(None, max_length=500, description="Updated loan notes")


class LoanRead(BaseModel):
    """
    Schema for returning loan data from the service or API layer.
    """
    id: UUID
    loan_number: str = Field(..., description="Unique loan identifier")
    borrower_id: UUID
    principal_amount: Decimal
    interest_rate: Decimal
    term_months: int
    currency_code: str
    start_date: date
    maturity_date: date
    product_type: str
    status: Literal["PENDING", "DISBURSED", "ACTIVE", "CLOSED", "DEFAULTED"]
    disbursement_account_id: UUID
    repayment_frequency: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ==================== SCHEDULE SCHEMAS ====================

class ScheduleCreate(BaseModel):
    """
    Schema for creating a loan repayment schedule.
    Validates input before schedule generation.
    """
    loan_id: UUID = Field(..., description="Loan ID this schedule belongs to")
    installments: int = Field(..., gt=0, description="Number of installments")
    start_date: date = Field(..., description="First installment due date")
    frequency: Literal["MONTHLY", "WEEKLY", "BIWEEKLY"] = Field(..., description="Payment frequency")


class ScheduleInstallmentRead(BaseModel):
    """
    Schema for reading a single schedule installment.
    """
    id: UUID
    loan_id: UUID
    installment_number: int = Field(..., description="Installment sequence number (1, 2, 3...)")
    due_date: date
    principal_amount: Decimal = Field(..., description="Principal component of this installment")
    interest_amount: Decimal = Field(..., description="Interest component of this installment")
    total_amount: Decimal = Field(..., description="Total amount due (principal + interest)")
    status: Literal["PENDING", "PAID", "OVERDUE", "PARTIALLY_PAID"] = Field(..., description="Installment status")
    paid_amount: Decimal = Field(default=Decimal("0"), description="Amount paid so far")
    paid_date: Optional[date] = Field(None, description="Date when fully paid")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class ScheduleRead(BaseModel):
    """
    Schema for reading a complete loan schedule.
    """
    loan_id: UUID
    total_installments: int
    total_principal: Decimal
    total_interest: Decimal
    total_amount: Decimal
    installments: list[ScheduleInstallmentRead]
    
    class Config:
        orm_mode = True


# ==================== DISBURSEMENT SCHEMAS ====================

class DisbursementCreate(BaseModel):
    """
    Schema for creating a loan disbursement.
    Validates input before fund transfer execution.
    """
    loan_id: UUID = Field(..., description="Loan ID to disburse")
    disbursement_amount: Decimal = Field(..., gt=0, description="Amount to disburse (must be positive)")
    disbursement_account_id: UUID = Field(..., description="Target account for disbursement")
    disbursement_date: date = Field(..., description="Disbursement execution date")
    payment_provider: str = Field(..., max_length=50, description="Payment provider (MTN, AIRTEL, BANK)")
    reference: Optional[str] = Field(None, max_length=100, description="External reference number")
    notes: Optional[str] = Field(None, max_length=255, description="Disbursement notes")
    
    @field_validator('disbursement_amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Disbursement amount must be positive")
        return v


class DisbursementRead(BaseModel):
    """
    Schema for reading a loan disbursement record.
    """
    id: UUID
    loan_id: UUID
    disbursement_amount: Decimal
    disbursement_account_id: UUID
    disbursement_date: date
    payment_provider: str
    status: Literal["PENDING", "COMPLETED", "FAILED", "CANCELLED"] = Field(..., description="Disbursement status")
    reference: Optional[str]
    payment_transaction_id: Optional[str] = Field(None, description="Payment system transaction ID")
    journal_entry_id: Optional[UUID] = Field(None, description="Accounting journal entry ID")
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ==================== REPAYMENT SCHEMAS ====================

class RepaymentCreate(BaseModel):
    """
    Schema for creating a loan repayment.
    Validates input before payment application.
    """
    loan_id: UUID = Field(..., description="Loan ID receiving payment")
    payment_amount: Decimal = Field(..., gt=0, description="Payment amount (must be positive)")
    payment_date: date = Field(..., description="Payment received date")
    payment_method: str = Field(..., max_length=50, description="Payment method (MOBILE_MONEY, BANK_TRANSFER, CASH)")
    payment_provider: Optional[str] = Field(None, max_length=50, description="Payment provider (MTN, AIRTEL, BANK)")
    reference: Optional[str] = Field(None, max_length=100, description="External payment reference")
    notes: Optional[str] = Field(None, max_length=255, description="Repayment notes")
    
    @field_validator('payment_amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be positive")
        return v


class RepaymentRead(BaseModel):
    """
    Schema for reading a loan repayment record.
    """
    id: UUID
    loan_id: UUID
    payment_amount: Decimal
    principal_applied: Decimal = Field(..., description="Amount applied to principal")
    interest_applied: Decimal = Field(..., description="Amount applied to interest")
    payment_date: date
    payment_method: str
    payment_provider: Optional[str]
    status: Literal["PENDING", "APPLIED", "REVERSED"] = Field(..., description="Repayment status")
    reference: Optional[str]
    payment_transaction_id: Optional[str] = Field(None, description="Payment system transaction ID")
    journal_entry_id: Optional[UUID] = Field(None, description="Accounting journal entry ID")
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# ==================== INTEREST CALCULATION SCHEMAS ====================

class InterestCalculationRequest(BaseModel):
    """
    Schema for requesting interest calculation.
    Pure calculation input - no database operations.
    """
    principal: Decimal = Field(..., gt=0, description="Principal amount")
    annual_rate: Decimal = Field(..., ge=0, le=100, description="Annual interest rate (0-100%)")
    term_months: int = Field(..., gt=0, description="Term in months")
    calculation_method: Literal["SIMPLE", "COMPOUND", "AMORTIZED"] = Field(
        default="AMORTIZED", description="Interest calculation method"
    )


class InterestCalculationResult(BaseModel):
    """
    Schema for interest calculation result.
    Pure calculation output - no database operations.
    """
    principal: Decimal
    total_interest: Decimal
    total_amount: Decimal
    monthly_payment: Optional[Decimal] = Field(None, description="Monthly payment for amortized loans")
    calculation_method: str
    calculated_at: datetime