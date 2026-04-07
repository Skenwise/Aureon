# database/engine.py
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

# ============================================================================
# SQLite Configuration
# ============================================================================

sqlite_engine = create_engine(
    "sqlite:///database/systemDatabase.db",
    echo=True, 
    connect_args={"check_same_thread": False}
)

sqlite_async_engine = create_async_engine(
    "sqlite+aiosqlite:///database/systemDatabase.db",
    echo=True
)

# ============================================================================
# PostgreSQL Configuration
# ============================================================================

postgres_engine = create_engine(
    "postgresql+psycopg2://postgres:Black99raiser%*@localhost:5432/loansystem",
    echo=True
)

postgres_async_engine = create_async_engine(
    "postgresql+asyncpg://postgres:Black99raiser%*@localhost:5432/loansystem",
    echo=True
)

# ============================================================================
# SQL Server Configuration (Optional - Commented out)
# ============================================================================
# Install pyodbc if needed: pip install pyodbc
# sqlserver_engine = create_engine(
#     "mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server",
#     echo=True
# )       
# sqlserver_async_engine = create_async_engine(
#     "mssql+asyncpyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server",
#     echo=True       
# )