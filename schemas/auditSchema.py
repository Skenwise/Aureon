# schemas/auditSchema.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


# ==================== AUDIT ENUMS ====================

class AuditAction(str, Enum):
    """
    Types of actions that can be audited.
    Each action represents a significant system event.
    """
    # CRUD Operations
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    
    # Financial Operations
    JOURNAL_POST = "JOURNAL_POST"
    JOURNAL_REVERSE = "JOURNAL_REVERSE"
    PAYMENT_EXECUTE = "PAYMENT_EXECUTE"
    PAYMENT_FAIL = "PAYMENT_FAIL"
    LOAN_DISBURSE = "LOAN_DISBURSE"
    LOAN_REPAY = "LOAN_REPAY"
    LOAN_WRITE_OFF = "LOAN_WRITE_OFF"
    LOAN_APPROVE = "LOAN_APPROVE"
    LOAN_REJECT = "LOAN_REJECT"
    
    # Treasury Operations
    LIQUIDITY_CHECK = "LIQUIDITY_CHECK"
    FUND_RESERVE = "FUND_RESERVE"
    FUND_RELEASE = "FUND_RELEASE"
    
    # Security
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    PERMISSION_CHANGE = "PERMISSION_CHANGE"
    ROLE_ASSIGN = "ROLE_ASSIGN"
    ROLE_REVOKE = "ROLE_REVOKE"
    
    # System
    SYSTEM_START = "SYSTEM_START"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    CONFIG_CHANGE = "CONFIG_CHANGE"


class AuditSeverity(str, Enum):
    """
    Severity level of the audited event.
    Used for filtering and alerting.
    """
    INFO = "INFO"           # Normal operations
    WARNING = "WARNING"     # Unusual but not critical
    ERROR = "ERROR"         # Failed operations
    CRITICAL = "CRITICAL"   # System integrity issues


# ==================== AUDIT LOG SCHEMAS ====================

class AuditLogCreate(BaseModel):
    """
    Schema for creating a new audit log entry.
    Captures all relevant context about an event.
    """
    tenant_id: UUID = Field(..., description="Tenant ID where the event occurred")
    user_id: Optional[UUID] = Field(None, description="User who performed the action")
    user_email: Optional[str] = Field(None, max_length=255, description="User email for context")
    ip_address: Optional[str] = Field(None, max_length=45, description="IP address of the requester")
    user_agent: Optional[str] = Field(None, max_length=500, description="User agent string")
    
    action: AuditAction = Field(..., description="Type of action performed")
    severity: AuditSeverity = Field(default=AuditSeverity.INFO, description="Severity level")
    
    entity_type: str = Field(..., max_length=100, description="Type of entity (e.g., 'loan', 'payment', 'user')")
    entity_id: Optional[UUID] = Field(None, description="ID of the entity being acted upon")
    entity_identifier: Optional[str] = Field(None, max_length=200, description="Human-readable entity identifier (e.g., 'LOAN-001')")
    
    old_data: Optional[Dict[str, Any]] = Field(None, description="Snapshot of data before change")
    new_data: Optional[Dict[str, Any]] = Field(None, description="Snapshot of data after change")
    
    reason: Optional[str] = Field(None, max_length=500, description="Reason for the action")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context or metadata")
    
    # Links to financial records
    journal_entry_id: Optional[UUID] = Field(None, description="Related journal entry ID")
    payment_id: Optional[UUID] = Field(None, description="Related payment ID")
    loan_id: Optional[UUID] = Field(None, description="Related loan ID")
    transaction_id: Optional[UUID] = Field(None, description="Related transaction ID")


class AuditLogRead(BaseModel):
    """
    Schema for returning audit log data from the service or API layer.
    """
    id: UUID
    tenant_id: UUID
    user_id: Optional[UUID]
    user_email: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    
    action: AuditAction
    severity: AuditSeverity
    
    entity_type: str
    entity_id: Optional[UUID]
    entity_identifier: Optional[str]
    
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    
    reason: Optional[str]
    metadata: Optional[Dict[str, Any]]
    
    journal_entry_id: Optional[UUID]
    payment_id: Optional[UUID]
    loan_id: Optional[UUID]
    transaction_id: Optional[UUID]
    
    created_at: datetime
    
    class Config:
        orm_mode = True


class AuditLogFilter(BaseModel):
    """
    Schema for filtering audit log queries.
    All fields are optional.
    """
    tenant_id: Optional[UUID] = Field(None, description="Filter by tenant")
    user_id: Optional[UUID] = Field(None, description="Filter by user")
    action: Optional[AuditAction] = Field(None, description="Filter by action type")
    severity: Optional[AuditSeverity] = Field(None, description="Filter by severity")
    entity_type: Optional[str] = Field(None, max_length=100, description="Filter by entity type")
    entity_id: Optional[UUID] = Field(None, description="Filter by entity ID")
    
    from_date: Optional[datetime] = Field(None, description="Start date for filter range")
    to_date: Optional[datetime] = Field(None, description="End date for filter range")
    
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")
    offset: int = Field(default=0, ge=0, description="Number of records to skip for pagination")


# ==================== RECONCILIATION SCHEMAS ====================

class ReconciliationStatus(str, Enum):
    """
    Status of a reconciliation record.
    """
    PENDING = "PENDING"
    RECONCILED = "RECONCILED"
    DISCREPANCY = "DISCREPANCY"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"


class ReconciliationType(str, Enum):
    """
    Type of reconciliation being performed.
    """
    BANK = "BANK"           # Bank statement reconciliation
    CASH = "CASH"           # Physical cash count
    LOAN = "LOAN"           # Loan portfolio reconciliation
    PROVIDER = "PROVIDER"   # Third-party provider (MTN, Airtel)
    INTERNAL = "INTERNAL"   # Inter-account reconciliation


class ReconciliationCreate(BaseModel):
    """
    Schema for creating a new reconciliation record.
    Used to track external vs internal balance matching.
    """
    tenant_id: UUID = Field(..., description="Tenant ID")
    reconciliation_type: ReconciliationType = Field(..., description="Type of reconciliation")
    reconciliation_date: datetime = Field(..., description="Date of reconciliation")
    
    beginning_balance: float = Field(..., description="System balance at period start")
    ending_balance: float = Field(..., description="System balance at period end")
    statement_balance: float = Field(..., description="External statement balance")
    difference: float = Field(..., description="Difference (ending_balance - statement_balance)")
    
    notes: Optional[str] = Field(None, max_length=1000, description="Reconciliation notes")
    reference: Optional[str] = Field(None, max_length=100, description="External reference (statement number, etc.)")
    
    @field_validator('difference')
    def validate_difference(cls, v):
        if v != 0:
            # Difference is allowed, but note it in validation
            pass
        return v


class ReconciliationUpdate(BaseModel):
    """
    Schema for updating an existing reconciliation record.
    """
    status: Optional[ReconciliationStatus] = Field(None, description="Updated reconciliation status")
    resolved_difference: Optional[float] = Field(None, description="Resolved difference amount after investigation")
    resolution_notes: Optional[str] = Field(None, max_length=1000, description="How the discrepancy was resolved")
    reconciled_by: Optional[UUID] = Field(None, description="User who completed reconciliation")


class ReconciliationRead(BaseModel):
    """
    Schema for returning reconciliation data from the service or API layer.
    """
    id: UUID
    tenant_id: UUID
    reconciliation_number: str = Field(..., description="Unique reconciliation identifier (RC-YYYYMMDD-XXXX)")
    reconciliation_type: ReconciliationType
    reconciliation_date: datetime
    
    beginning_balance: float
    ending_balance: float
    statement_balance: float
    difference: float
    resolved_difference: Optional[float]
    
    status: ReconciliationStatus
    notes: Optional[str]
    reference: Optional[str]
    resolution_notes: Optional[str]
    
    created_by: Optional[UUID]
    reconciled_by: Optional[UUID]
    reconciled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True