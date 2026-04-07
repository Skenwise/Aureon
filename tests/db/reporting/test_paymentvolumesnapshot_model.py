# tests/db/reporting/test_paymentvolumesnapshot_model.py
"""Integration tests for PaymentVolumeSnapshot model using isolated database harness."""

from datetime import date
from decimal import Decimal

from database.model.core.company import Company
from database.model.reporting.payment_volume import PaymentVolumeSnapshot


def test_create_payment_volume_snapshot(db_session):
    """Create a valid PaymentVolumeSnapshot record and verify it persists correctly."""
    company = Company(code="VOLCO", name="Volume Company")
    db_session.add(company)
    db_session.commit()

    snapshot = PaymentVolumeSnapshot(
        tenant_id=company.id,
        snapshot_date=date.today(),
        provider="MTN",
        total_transactions=150,
        total_volume=Decimal("5000.00"),
        successful=145,
        failed=5,
        average_response_ms=120.5
    )
    db_session.add(snapshot)
    db_session.commit()

    retrieved = db_session.get(PaymentVolumeSnapshot, snapshot.id)
    assert retrieved is not None
    assert retrieved.provider == "MTN"
    assert retrieved.total_transactions == 150
    assert retrieved.successful == 145
    assert retrieved.average_response_ms == 120.5