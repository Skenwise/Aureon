"""
Journal data provider.

Provides database access for Journal model.
Supports deterministic creation, retrieval, and listing of journals.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.model.finance.journal import Journal
from backend.core.error import NotFoundError, CalculationError


class JournalProvider:
    """
    Provider for ledger journal queries and operations.

    Encapsulates all database logic for journals. All operations
    are deterministic and validated before returning results.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the provider with a database session.

        Args:
            session (AsyncSession): SQLAlchemy async session for DB operations.
        """
        self.session = session

    # ----------------- Journal Operations ----------------- #

    async def create_journal(self, journal: Journal) -> Journal:
        """
        Persist a new journal entry in the database.

        Args:
            journal (Journal): Journal object to persist.

        Returns:
            Journal: The created journal with ID and timestamps.

        Raises:
            ValueError: If a journal with the same reference already exists.
        """
        stmt = select(Journal).where(Journal.reference == journal.reference)
        result = await self.session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError(f"Journal with reference {journal.reference} already exists.")

        self.session.add(journal)
        await self.session.commit()
        await self.session.refresh(journal)
        return journal

    async def get_journal(self, journal_id: UUID) -> Journal:
        """
        Retrieve a journal entry by its unique ID.

        Args:
            journal_id (UUID): Journal identifier.

        Returns:
            Journal: Journal object with postings.

        Raises:
            NotFoundError: If no journal exists with the given ID.
        """
        stmt = select(Journal).where(Journal.id == journal_id)
        result = await self.session.execute(stmt)
        journal = result.scalar_one_or_none()
        if not journal:
            raise NotFoundError("Journal", str(journal_id))
        return journal

    async def list_journals(self, source: Optional[str] = None) -> List[Journal]:
        """
        List all journal entries, optionally filtered by source.

        Args:
            source (str, optional): Source system/module to filter journals.

        Returns:
            List[Journal]: All matching journal entries.
        """
        stmt = select(Journal)
        if source:
            stmt = stmt.where(Journal.source == source)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
