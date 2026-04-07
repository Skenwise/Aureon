# tests/test_db_base_model.py
import uuid
from sqlmodel import SQLModel, Field
from sqlalchemy.orm import Session


class DummyModel(SQLModel, table=True):
    """Temporary model to test the isolation harness."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(..., max_length=100)


def test_create_dummy_model(db_session: Session):
    """Verify we can create and retrieve a model in an isolated database."""
    dummy = DummyModel(name="test_model")
    db_session.add(dummy)
    db_session.commit()
    
    retrieved = db_session.get(DummyModel, dummy.id)
    assert retrieved is not None
    assert retrieved.name == "test_model"


def test_db_isolation(db_session: Session):
    """Verify that database state does not leak between tests.
    
    This test relies on the fixture to destroy the database after each test.
    If state leaked, this test would see the DummyModel from the previous test.
    """
    dummy = DummyModel(name="isolated_test")
    db_session.add(dummy)
    db_session.commit()
    
    assert db_session.query(DummyModel).count() == 1


def test_previous_test_left_no_data(db_session: Session):
    """Prove that no data persists from previous tests.
    
    If this fails, the isolation layer is broken.
    """
    count = db_session.query(DummyModel).count()
    assert count == 0