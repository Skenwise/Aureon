# Middleware/DataProvider/JournalProvider/journalProvider.py
"""
Journal data provider.

Provides database access for Journal model.
Supports deterministic creation, retrieval, and listing of journals.
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import select, Session
from database.model.finance.journal import Journal
from backend.core.error import NotFoundError, CalculationError


class JournalProvider:
    """
    Provider for ledger journal queries and operations.

    Encapsulates all database logic for journals. All operations
    are deterministic and validated before returning results.
    """

    def __init__(self, session: Session):
        """
        Initialize the provider with a database session.

        Args:
            session (Session): SQLModel session for DB operations.
        """
        self.session = session

    # ----------------- Journal Operations ----------------- #

    def create_journal(self, journal: Journal) -> Journal:
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
        existing = self.session.exec(stmt).first()
        if existing:
            raise ValueError(f"Journal with reference {journal.reference} already exists.")

        self.session.add(journal)
        self.session.commit()
        self.session.refresh(journal)
        return journal

    def get_journal(self, journal_id: UUID) -> Journal:
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
        journal = self.session.exec(stmt).first()
        if not journal:
            raise NotFoundError("Journal", str(journal_id))
        return journal

    def list_journals(self, source: Optional[str] = None) -> List[Journal]:
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
        return list(self.session.exec(stmt).all())
