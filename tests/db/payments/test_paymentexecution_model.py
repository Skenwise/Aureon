# tests/db/payments/test_paymentexecution_model.py
"""Integration tests for PaymentExecution model using isolated database harness."""

from datetime import datetime, timezone

from database.model.core.company import Company
from database.model.misc.currency import Currency
from database.model.payments.payment import Payment
from database.model.payments.payment_execution import PaymentExecution


def test_create_payment_execution(db_session):
    """Create a valid PaymentExecution record and verify it persists correctly."""
    # Create dependencies
    currency = Currency(code="USD", name="US Dollar", decimals=2)
    company = Company(code="EXECCO", name="Execution Company")
    payment = Payment(
        payment_number="EXEC-001",
        payment_type="OUTBOUND",
        direction="OUT",
        amount=100,
        currency="USD",
        provider_type="INTERNAL"
    )
    
    db_session.add_all([currency, company, payment])
    db_session.commit()

    execution = PaymentExecution(
        payment_id=payment.id,
        attempt_number=1,
        status="SUCCESS",
        provider_transaction_id="TX123456",
        executed_at=datetime.now(timezone.utc)
    )
    db_session.add(execution)
    db_session.commit()

    retrieved = db_session.get(PaymentExecution, execution.id)
    assert retrieved is not None
    assert retrieved.attempt_number == 1
    assert retrieved.status == "SUCCESS"
    assert retrieved.provider_transaction_id == "TX123456"


def test_payment_execution_relationships(db_session):
    """Test PaymentExecution to Payment relationship."""
    currency = Currency(code="ZMW", name="Zambian Kwacha", decimals=2)
    company = Company(code="RELEXEC", name="Relationship Execution Co")
    payment = Payment(
        payment_number="RELEXEC-001",
        payment_type="OUTBOUND",
        direction="OUT",
        amount=50,
        currency="ZMW",
        provider_type="INTERNAL"
    )
    
    db_session.add_all([currency, company, payment])
    db_session.commit()

    execution = PaymentExecution(
        payment_id=payment.id,
        attempt_number=1,
        status="SUCCESS"
    )
    db_session.add(execution)
    db_session.commit()

    assert execution.payment is not None
    assert execution.payment.id == payment.id
    assert execution.payment.payment_number == "RELEXEC-001"