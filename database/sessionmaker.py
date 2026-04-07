# database/sessionmaker.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from database.engine import (
    sqlite_engine, 
    sqlite_async_engine, 
    postgres_engine, 
    postgres_async_engine
)
from typing import AsyncGenerator
from contextlib import contextmanager, asynccontextmanager


#------------------------------------------
# SESSION MAKER
#-----------------------------------------

SqliteSessionLocal = sessionmaker(
    bind=sqlite_engine,
    autoflush=False,
    autocommit=False
)

PostgresSessionLocal = sessionmaker(
    bind=postgres_engine,
    autoflush=False,
    autocommit=False
)

SqliteAsyncSessionLocal = async_sessionmaker(
    sqlite_async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

PostgresAsyncSessionLocal = async_sessionmaker(
    postgres_async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


#-----------------------------------
# SYNC CONTEXT MANAGERS
#---------------------------------

@contextmanager
def get_sqlite_db_session():
    db = SqliteSessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_postgres_db_session():
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()


#-----------------------------------
# ASYNC GENERATORS (for FastAPI Depends)
#-----------------------------------

async def get_sqlite_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session generator for FastAPI dependencies (SQLite).
    """
    async with SqliteAsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_postgres_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session generator for FastAPI dependencies (PostgreSQL).
    """
    async with PostgresAsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Alias for default async session (using PostgreSQL)
get_async_db_session = get_postgres_async_db_session