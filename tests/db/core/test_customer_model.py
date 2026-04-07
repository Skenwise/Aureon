# tests/db/test_customer_model.py
"""Integration tests for Customer model using isolated database harness."""

import pytest
from sqlalchemy.exc import IntegrityError

from database.model.core.company import Company
from database.model.core.customer import Customer


def test_create_customer(db_session):
    """Create a valid Customer record and verify it persists correctly."""
    # First create a company (parent record)
    company = Company(code="CUSTCO", name="Customer Company")
    db_session.add(company)
    db_session.commit()

    customer = Customer(
        external_customer_ref="EXT001",
        first_name="John",
        last_name="Doe",
        phone="+260977123456",
        email="john.doe@example.com",
        kyc_status="verified",
        company_id=company.id
    )
    db_session.add(customer)
    db_session.commit()

    retrieved = db_session.get(Customer, customer.id)
    assert retrieved is not None
    assert retrieved.first_name == "John"
    assert retrieved.last_name == "Doe"
    assert retrieved.email == "john.doe@example.com"
    assert retrieved.kyc_status == "verified"
    assert retrieved.company_id == company.id


def test_customer_relationships(db_session):
    """Test Customer to Company relationship works correctly."""
    # Create parent Company
    company = Company(code="RELCO", name="Relationship Company")
    db_session.add(company)
    db_session.commit()

    # Create Customer linked to Company
    customer = Customer(
        first_name="Jane",
        last_name="Smith",
        company_id=company.id
    )
    db_session.add(customer)
    db_session.commit()

    # Verify relationship
    assert customer.company is not None
    assert customer.company.id == company.id
    assert customer.company.name == "Relationship Company"