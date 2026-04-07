"""
Isolated test harness for Aureon database tests.
"""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlmodel import SQLModel


@pytest.fixture(scope="function")
async def db_session():
    """Provides an async database session for each test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
        await session.rollback()
    
    await engine.dispose()
