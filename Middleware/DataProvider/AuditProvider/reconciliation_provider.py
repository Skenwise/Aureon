"""
Reconciliation Data Provider.

Provides database access for Reconciliation model.
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import select, Session, desc, and_
from datetime import date, datetime

from database.model.audit.reconciliation import Reconciliation
from backend.core.error import NotFoundError


class ReconciliationProvider:
    """
    Provider for reconciliation queries and operations.
    
    Senior Tip: Reconciliations prove the system was balanced at a point in time.
    Always query by tenant_id first.
    """

    def __init__(self, session: Session):
        self.session = session

    # ----------------- Create ----------------- #

    def create_reconciliation(self, reconciliation: Reconciliation) -> Reconciliation:
        """Create a reconciliation record."""
        self.session.add(reconciliation)
        self.session.commit()
        self.session.refresh(reconciliation)
        return reconciliation

    # ----------------- Read ----------------- #

    def get_reconciliation(self, rec_id: UUID) -> Reconciliation:
        """Get reconciliation by ID."""
        stmt = select(Reconciliation).where(Reconciliation.id == rec_id)
        rec = self.session.exec(stmt).first()
        if not rec:
            raise NotFoundError("Reconciliation", str(rec_id))
        return rec

    def get_reconciliation_by_date(self, business_date: date, tenant_id: UUID) -> Optional[Reconciliation]:
        """Get reconciliation for specific date and tenant."""
        stmt = select(Reconciliation).where(
            Reconciliation.business_date == business_date,
            Reconciliation.tenant_id == tenant_id
        )
        return self.session.exec(stmt).first()

    def list_reconciliations_by_tenant(
        self, 
        tenant_id: UUID, 
        balanced: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Reconciliation]:
        """
        List reconciliations for a tenant.
        
        Senior Tip: Use 'balanced' parameter to find discrepancies quickly.
        """
        conditions = [Reconciliation.tenant_id == tenant_id]
        
        if balanced is not None:
            conditions.append(Reconciliation.balanced == balanced)

        stmt = (
            select(Reconciliation)
            .where(and_(*conditions))
            .order_by(desc(Reconciliation.business_date))
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(stmt).all())

    # ----------------- Update ----------------- #

    def update_reconciliation(self, rec_id: UUID, updated_fields: dict) -> Reconciliation:
        """Update reconciliation record."""
        rec = self.get_reconciliation(rec_id)
        
        for key, value in updated_fields.items():
            if hasattr(rec, key):
                setattr(rec, key, value)
        
        self.session.add(rec)
        self.session.commit()
        self.session.refresh(rec)
        return rec