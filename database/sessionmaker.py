from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from engine import sqlite_engine, sqlite_async_engine, postgres_engine, postgres_async_engine
from typing import AsyncGenerator
from contextlib import contextmanager, asynccontextmanager


#------------------------------------------
# SESSION MAKER
#-----------------------------------------

SqliteSessionLocal = sessionmaker(
    bind=sqlite_engine,
    autoflush = False,
    autocommit = False
)

PostgresSessionLocal = sessionmaker(
    bind = postgres_engine,
    autoflush = False,
    autocommit = False
)

SqliteAsyncSessionLocal = async_sessionmaker(
    sqlite_async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

PostgresAsyncSessionLocal = async_sessionmaker(
    postgres_async_engine,
    class_ = AsyncSession,
    expire_on_commit = False
)


#-----------------------------------
# CONTEXT MANAGER
#---------------------------------


# Sqlite synchronous session
@contextmanager
def get_sqlite_db_session():
    db = SqliteSessionLocal()

    try:
        yield db
    finally:
        db.close()

# Postgres synchronous session
@contextmanager
def get_postgres_db_session():
    db = PostgresSessionLocal()

    try:
        yield db
    finally:
        db.close()

# Sqlite asynchronous session
@asynccontextmanager
async def get_sqlite_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SqliteAsyncSessionLocal() as session:
        yield session

# Postgres asynchronous session
@asynccontextmanager
async def get_postgres_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with PostgresAsyncSessionLocal() as session:
        yield session