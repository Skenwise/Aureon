# backend/Accounting/journal.py

"""
Journal Port & Adapter.

Defines core ledger journal operations and delegates to JournalProvider.
"""

from typing import List, Protocol, Any, cast
from uuid import UUID
from schemas.journalSchema import JournalCreate, JournalRead
from backend.core.error import NotFoundError
from Middleware.DataProvider.AccountProvider.journalProvider import JournalProvider


class JournalPort(Protocol):
    """
    Port interface for ledger journal operations.

    All operations are deterministic, validated, and raise domain errors
    when necessary. No provider or infra logic should be handled here.
    """

    def create_journal(self, journal_in: JournalCreate) -> JournalRead:
        """
        Create a new journal entry with associated postings.

        Args:
            journal_in (JournalCreate): Input data for the journal entry.

        Returns:
            JournalRead: The created journal entry.

        Raises:
            ValueError: If double-entry invariants are violated.
        """
        raise NotImplementedError

    def get_journal(self, journal_id: UUID) -> JournalRead:
        """
        Retrieve a journal entry by its unique ID.

        Args:
            journal_id (UUID): Ledger journal identifier.

        Returns:
            JournalRead: Journal entry with postings.

        Raises:
            NotFoundError: If the journal does not exist.
        """
        raise NotImplementedError

    def list_journals(self, source: str | None = None) -> List[JournalRead]:
        """
        List all journal entries, optionally filtered by source.

        Args:
            source (str, optional): Filter journals by source system/module.

        Returns:
            List[JournalRead]: All matching journal entries.
        """
        raise NotImplementedError


class JournalAdapter(JournalPort):
    """
    Adapter implementation of JournalPort.

    Delegates all ledger journal operations to JournalProvider
    and converts models to/from Pydantic schemas.
    """

    def __init__(self, provider: JournalProvider):
        """
        Initialize the adapter with a provider.

        Args:
            provider (JournalProvider): The data provider for journal operations.
        """
        self.provider = provider

    def create_journal(self, journal_in: JournalCreate) -> JournalRead:
        """
        Create a new journal entry via the provider.
        """
        journal_model = self.provider.create_journal(cast(Any, journal_in))
        return JournalRead.model_validate(journal_model)

    def get_journal(self, journal_id: UUID) -> JournalRead:
        """
        Retrieve a journal entry by ID via the provider.
        """
        journal_model = self.provider.get_journal(journal_id)
        return JournalRead.model_validate(journal_model)

    def list_journals(self, source: str | None = None ) -> List[JournalRead]:
        """
        List all journal entries via the provider, optionally filtered by source.
        """
        journals = self.provider.list_journals(source)
        return [JournalRead.model_validate(j) for j in journals]
