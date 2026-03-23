#backend/audit/reconciliation.py

"""
Reconciliation Port & Adapter.

Defines reconciliation operations for matching external vs internal balances.
"""

from typing import List, Protocol, Any, cast, Optional
from uuid import UUID
from schemas.auditSchema import (
    ReconciliationCreate,
    ReconciliationRead,
    ReconciliationUpdate,
    ReconciliationStatus
)
from backend.audit.errors import ReconciliationError
from backend.core.error import NotFoundError
from Middleware.DataProvider.AuditProvider.reconciliation_provider import ReconciliationProvider


class ReconciliationPort(Protocol):
    """
    Port interface for reconciliation operations.
    """

    def create_reconciliation(self, rec_in: ReconciliationCreate) -> ReconciliationRead:
        """Create a new reconciliation record."""
        raise NotImplementedError

    def get_reconciliation(self, rec_id: UUID) -> ReconciliationRead:
        """Retrieve a reconciliation by ID."""
        raise NotImplementedError

    def update_reconciliation(self, rec_id: UUID, rec_in: ReconciliationUpdate) -> ReconciliationRead:
        """Update an existing reconciliation."""
        raise NotImplementedError

    def list_reconciliations_by_tenant(
        self, 
        tenant_id: UUID, 
        status: Optional[ReconciliationStatus] = None
    ) -> List[ReconciliationRead]:
        """List reconciliations for a tenant, optionally filtered by status."""
        raise NotImplementedError


class ReconciliationAdapter(ReconciliationPort):
    """
    Adapter implementation of ReconciliationPort.
    """

    def __init__(self, provider: ReconciliationProvider):
        self.provider = provider

    def create_reconciliation(self, rec_in: ReconciliationCreate) -> ReconciliationRead:
        """Create a reconciliation record via the provider."""
        try:
            rec_model = self.provider.create_reconciliation(cast(Any, rec_in))
            return ReconciliationRead.model_validate(rec_model)
        except Exception as e:
            raise ReconciliationError(f"Failed to create reconciliation: {str(e)}")

    def get_reconciliation(self, rec_id: UUID) -> ReconciliationRead:
        """Retrieve a reconciliation by ID via the provider."""
        rec_model = self.provider.get_reconciliation(rec_id)
        return ReconciliationRead.model_validate(rec_model)

    def update_reconciliation(self, rec_id: UUID, rec_in: ReconciliationUpdate) -> ReconciliationRead:
        """Update a reconciliation record via the provider."""
        updated_fields = rec_in.model_dump(exclude_unset=True)
        rec_model = self.provider.update_reconciliation(rec_id, updated_fields)
        return ReconciliationRead.model_validate(rec_model)

    def list_reconciliations_by_tenant(
        self, 
        tenant_id: UUID, 
        status: Optional[ReconciliationStatus] = None
    ) -> List[ReconciliationRead]:
        """
        List reconciliations for a tenant via the provider.
        
        Senior Tip: Translate domain enum to storage primitive.
        - RECONCILED → balanced=True
        - DISCREPANCY → balanced=False
        - PENDING/INVESTIGATING → balanced=None (both)
        """
        # Translate status enum to balanced boolean
        balanced = None
        if status == ReconciliationStatus.RECONCILED:
            balanced = True
        elif status == ReconciliationStatus.DISCREPANCY:
            balanced = False
        # PENDING and INVESTIGATING return both (balanced=None)
        
        recs = self.provider.list_reconciliations_by_tenant(
            tenant_id, 
            balanced=balanced
        )
        return [ReconciliationRead.model_validate(rec) for rec in recs]