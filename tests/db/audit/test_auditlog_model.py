# tests/db/audit/test_auditlog_model.py
"""Integration tests for AuditLog model using isolated database harness."""

from datetime import datetime, timezone
import json

from database.model.core.company import Company
from database.model.core.user import User
from database.model.security.role import SecurityRole
from database.model.audit.audit_log import AuditLog


def test_create_audit_log(db_session):
    """Create a valid AuditLog record and verify it persists correctly."""
    # Create dependencies
    company = Company(code="AUDITCO", name="Audit Company")
    role = SecurityRole(name="auditor", is_default=False)
    user = User(username="audituser", email="audit@example.com", hashed_password="hash", role_id=role.id)
    
    db_session.add_all([company, role, user])
    db_session.commit()

    changes_json = json.dumps({"old_status": "pending", "new_status": "approved"})

    audit_log = AuditLog(
        tenant_id=company.id,
        entity="loan",
        entity_id=company.id,
        action="UPDATE",
        performed_by=user.id,
        ip_address="192.168.1.100",
        changes=changes_json,
        metadata_='{"source": "web"}'
    )
    db_session.add(audit_log)
    db_session.commit()

    retrieved = db_session.get(AuditLog, audit_log.id)
    assert retrieved is not None
    assert retrieved.entity == "loan"
    assert retrieved.action == "UPDATE"
    assert retrieved.ip_address == "192.168.1.100"


def test_audit_log_relationships(db_session):
    """Test AuditLog to Company and User relationships."""
    company = Company(code="RELAUDIT", name="Relationship Audit Co")
    role = SecurityRole(name="viewer", is_default=True)
    user = User(username="relaudit", email="rel@example.com", hashed_password="hash", role_id=role.id)
    
    db_session.add_all([company, role, user])
    db_session.commit()

    audit_log = AuditLog(
        tenant_id=company.id,
        entity="payment",
        entity_id=company.id,
        action="CREATE",
        performed_by=user.id
    )
    db_session.add(audit_log)
    db_session.commit()

    # Verify relationships
    assert audit_log.tenant_id == company.id
    assert audit_log.performed_by == user.id