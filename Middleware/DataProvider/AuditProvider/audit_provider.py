"""
Audit Data Provider.

Provides database access for AuditLog model.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from datetime import datetime

from database.model.audit.audit_log import AuditLog
from backend.core.error import NotFoundError
from schemas.auditSchema import AuditLogFilter


class AuditProvider:
    """
    Provider for audit log queries and operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ----------------- Create ----------------- #

    async def create_log(self, audit_log: AuditLog) -> AuditLog:
        """Create an immutable audit log entry."""
        self.session.add(audit_log)
        await self.session.commit()
        await self.session.refresh(audit_log)
        return audit_log

    # ----------------- Read ----------------- #

    async def get_log(self, log_id: UUID) -> AuditLog:
        """Retrieve audit log by ID."""
        stmt = select(AuditLog).where(AuditLog.id == log_id)
        result = await self.session.execute(stmt)
        log = result.scalar_one_or_none()
        if not log:
            raise NotFoundError("AuditLog", str(log_id))
        return log

    async def get_logs_by_tenant(self, tenant_id: UUID, limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """Retrieve audit logs for a specific tenant."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(desc(AuditLog.performed_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def filter_logs(self, filter_params: AuditLogFilter) -> List[AuditLog]:
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
            .order_by(desc(AuditLog.performed_at))
            .offset(filter_params.offset)
            .limit(filter_params.limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_entity_history(self, entity_type: str, entity_id: UUID) -> List[AuditLog]:
        """Get complete audit history for a specific entity."""
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.entity == entity_type,
                AuditLog.entity_id == entity_id
            )
            .order_by(desc(AuditLog.performed_at))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
