#backend/audit/audit.py

"""
Audit Port & Adapter.

Defines core audit logging operations and delegates to AuditProvider.
"""

from typing import List, Protocol, Any, cast
from uuid import UUID
from schemas.auditSchema import AuditLogCreate, AuditLogRead, AuditLogFilter
from backend.audit.errors import AuditLogError
from backend.core.error import NotFoundError
from Middleware.DataProvider.AuditProvider.audit_provider import AuditProvider


class AuditPort(Protocol):
    """
    Port interface for audit logging operations.

    All audit entries are append-only. No updates or deletions.
    Each entry captures who, what, when, where, why, and before/after state.
    """

    def log(self, log_in: AuditLogCreate) -> AuditLogRead:
        """
        Create an audit log entry.

        Args:
            log_in (AuditLogCreate): Audit log data with context.

        Returns:
            AuditLogRead: The created audit log entry.

        Raises:
            AuditLogError: If log creation fails.
        """
        raise NotImplementedError

    def get_log(self, log_id: UUID) -> AuditLogRead:
        """
        Retrieve an audit log by its unique ID.

        Args:
            log_id (UUID): Audit log identifier.

        Returns:
            AuditLogRead: Audit log entry.

        Raises:
            NotFoundError: If the log does not exist.
        """
        raise NotImplementedError

    def get_logs_by_tenant(self, tenant_id: UUID, limit: int = 100, offset: int = 0) -> List[AuditLogRead]:
        """
        Retrieve audit logs for a specific tenant.

        Args:
            tenant_id (UUID): Tenant identifier.
            limit (int): Maximum number of records to return.
            offset (int): Number of records to skip.

        Returns:
            List[AuditLogRead]: List of audit log entries.
        """
        raise NotImplementedError

    def filter_logs(self, filter_params: AuditLogFilter) -> List[AuditLogRead]:
        """
        Filter audit logs by multiple criteria.

        Args:
            filter_params (AuditLogFilter): Filter conditions.

        Returns:
            List[AuditLogRead]: Filtered audit log entries.
        """
        raise NotImplementedError

    def get_entity_history(self, entity_type: str, entity_id: UUID) -> List[AuditLogRead]:
        """
        Get complete audit history for a specific entity.

        Args:
            entity_type (str): Type of entity (e.g., 'loan', 'payment').
            entity_id (UUID): Entity identifier.

        Returns:
            List[AuditLogRead]: Chronological history of the entity.
        """
        raise NotImplementedError


class AuditAdapter(AuditPort):
    """
    Adapter implementation of AuditPort.

    Delegates all audit operations to AuditProvider and converts
    models to/from Pydantic schemas.
    """

    def __init__(self, provider: AuditProvider):
        """
        Initialize the adapter with a provider.

        Args:
            provider (AuditProvider): The data provider for audit operations.
        """
        self.provider = provider

    def log(self, log_in: AuditLogCreate) -> AuditLogRead:
        """
        Create an audit log entry via the provider.

        Architecture Note:
            Audit logging is append-only and should be the last operation
            after all business logic succeeds. This ensures we only log
            successful operations, never partial failures.
        """
        try:
            log_model = self.provider.create_log(cast(Any, log_in))
            return AuditLogRead.model_validate(log_model)
        except Exception as e:
            raise AuditLogError(f"Failed to create audit log: {str(e)}")

    def get_log(self, log_id: UUID) -> AuditLogRead:
        """
        Retrieve an audit log by ID via the provider.
        """
        log_model = self.provider.get_log(log_id)
        return AuditLogRead.model_validate(log_model)

    def get_logs_by_tenant(self, tenant_id: UUID, limit: int = 100, offset: int = 0) -> List[AuditLogRead]:
        """
        Retrieve tenant audit logs via the provider.
        """
        logs = self.provider.get_logs_by_tenant(tenant_id, limit, offset)
        return [AuditLogRead.model_validate(log) for log in logs]

    def filter_logs(self, filter_params: AuditLogFilter) -> List[AuditLogRead]:
        """
        Filter audit logs via the provider.
        """
        logs = self.provider.filter_logs(filter_params)
        return [AuditLogRead.model_validate(log) for log in logs]

    def get_entity_history(self, entity_type: str, entity_id: UUID) -> List[AuditLogRead]:
        """
        Get entity history via the provider.

        Architecture Note:
            This returns the complete state change history of any entity.
            Used for compliance reporting, dispute resolution, and debugging.
        """
        logs = self.provider.get_entity_history(entity_type, entity_id)
        return [AuditLogRead.model_validate(log) for log in logs]