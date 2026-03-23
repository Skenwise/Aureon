#Middleware/DataProvider/AuditProvider/audit_provider.py

"""
Audit Data Provider.

Provides database access for AuditLog model.
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import select, Session, and_  # ✅ Remove desc from import
from datetime import datetime

from database.model.audit.audit_log import AuditLog
from backend.core.error import NotFoundError
from schemas.auditSchema import AuditLogFilter
from sqlmodel import desc  # ✅ Import desc here for use in queries

class AuditProvider:
    """
    Provider for audit log queries and operations.
    """

    def __init__(self, session: Session):
        self.session = session

    # ----------------- Create ----------------- #

    def create_log(self, audit_log: AuditLog) -> AuditLog:
        """Create an immutable audit log entry."""
        self.session.add(audit_log)
        self.session.commit()
        self.session.refresh(audit_log)
        return audit_log

    # ----------------- Read ----------------- #

    def get_log(self, log_id: UUID) -> AuditLog:
        """Retrieve audit log by ID."""
        stmt = select(AuditLog).where(AuditLog.id == log_id)
        log = self.session.exec(stmt).first()
        if not log:
            raise NotFoundError("AuditLog", str(log_id))
        return log

    def get_logs_by_tenant(self, tenant_id: UUID, limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """Retrieve audit logs for a specific tenant."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.performed_at.desc())  # type: ignore
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.exec(stmt).all())

    def filter_logs(self, filter_params: AuditLogFilter) -> List[AuditLog]:
        """Filter audit logs by multiple criteria."""
        conditions = [AuditLog.tenant_id == filter_params.tenant_id]
        
        if filter_params.user_id:
            conditions.append(AuditLog.performed_by == filter_params.user_id)
        if filter_params.action:
            conditions.append(AuditLog.action == filter_params.action.value)
        if filter_params.entity_type:
            conditions.append(AuditLog.entity == filter_params.entity_type)
        if filter_params.entity_id:
            conditions.append(AuditLog.entity_id == filter_params.entity_id)
        if filter_params.from_date:
            conditions.append(AuditLog.performed_at >= filter_params.from_date)
        if filter_params.to_date:
            conditions.append(AuditLog.performed_at <= filter_params.to_date)

        stmt = (
            select(AuditLog)
            .where(and_(*conditions))
            .order_by(AuditLog.performed_at.desc())  # type: ignore
            .offset(filter_params.offset)
            .limit(filter_params.limit)
        )
        return list(self.session.exec(stmt).all())

    def get_entity_history(self, entity_type: str, entity_id: UUID) -> List[AuditLog]:
        """Get complete audit history for a specific entity."""
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.entity == entity_type,
                AuditLog.entity_id == entity_id
            )
            .order_by(AuditLog.performed_at.desc())  # type: ignore
        )
        return list(self.session.exec(stmt).all())