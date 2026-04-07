# tests/conftest.py
# ISOLATION LAYER: State destroyed after every test function.

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlmodel import SQLModel


@pytest.fixture(scope="function", name="db_session")
def db_session_fixture():
    """Provides a clean database session for each test.
    
    Creates an in-memory SQLite database with all tables.
    Destroys all data and closes the connection after the test finishes.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    
    session = Session(engine)
    
    try:
        yield session
    finally:
        session.close()
        SQLModel.metadata.drop_all(engine)
        engine.dispose()