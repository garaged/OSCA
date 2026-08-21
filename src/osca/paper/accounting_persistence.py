"""Append-only SQLite persistence for D8 virtual-portfolio accounting."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import UUID

from osca.paper.accounting_contracts import (
    AccountingEvent,
    JournalTransaction,
    ValuationObservation,
    VirtualPortfolio,
)


class AccountingPersistenceError(RuntimeError):
    """Base error for accounting persistence failures."""


class AccountingConflictError(AccountingPersistenceError):
    """Raised when an immutable identity is reused with different content."""


class AccountingNotFoundError(AccountingPersistenceError):
    """Raised when requested accounting evidence does not exist."""


class SQLitePortfolioAccountingStore:
    """Profile-scoped append-only store for accounting authority and valuation evidence."""

    SCHEMA_VERSION = 1

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS accounting_schema (
                    singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                    version INTEGER NOT NULL
                );

                INSERT OR IGNORE INTO accounting_schema(singleton, version) VALUES(1, 1);

                CREATE TABLE IF NOT EXISTS virtual_portfolios (
                    portfolio_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS accounting_events (
                    event_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    source_kind TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    content_digest TEXT NOT NULL,
                    effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    FOREIGN KEY(portfolio_id) REFERENCES virtual_portfolios(portfolio_id),
                    UNIQUE(portfolio_id, sequence),
                    UNIQUE(portfolio_id, source_kind, source_id)
                );

                CREATE TABLE IF NOT EXISTS journal_transactions (
                    transaction_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    event_id TEXT NOT NULL UNIQUE,
                    effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    FOREIGN KEY(portfolio_id) REFERENCES virtual_portfolios(portfolio_id),
                    FOREIGN KEY(event_id) REFERENCES accounting_events(event_id)
                );

                CREATE TABLE IF NOT EXISTS valuation_observations (
                    observation_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    asset_id TEXT NOT NULL,
                    valuation_revision TEXT NOT NULL,
                    price_effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    FOREIGN KEY(portfolio_id) REFERENCES virtual_portfolios(portfolio_id),
                    UNIQUE(portfolio_id, asset_id, valuation_revision)
                );

                CREATE INDEX IF NOT EXISTS idx_accounting_events_portfolio_sequence
                    ON accounting_events(portfolio_id, sequence);
                CREATE INDEX IF NOT EXISTS idx_journal_portfolio_effective
                    ON journal_transactions(portfolio_id, effective_at, transaction_id);
                CREATE INDEX IF NOT EXISTS idx_valuation_portfolio_asset_effective
                    ON valuation_observations(portfolio_id, asset_id, price_effective_at);

                CREATE TRIGGER IF NOT EXISTS accounting_events_no_update
                BEFORE UPDATE ON accounting_events BEGIN
                    SELECT RAISE(ABORT, 'accounting_events is append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS accounting_events_no_delete
                BEFORE DELETE ON accounting_events BEGIN
                    SELECT RAISE(ABORT, 'accounting_events is append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS journal_transactions_no_update
                BEFORE UPDATE ON journal_transactions BEGIN
                    SELECT RAISE(ABORT, 'journal_transactions is append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS journal_transactions_no_delete
                BEFORE DELETE ON journal_transactions BEGIN
                    SELECT RAISE(ABORT, 'journal_transactions is append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS valuation_observations_no_update
                BEFORE UPDATE ON valuation_observations BEGIN
                    SELECT RAISE(ABORT, 'valuation_observations is append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS valuation_observations_no_delete
                BEFORE DELETE ON valuation_observations BEGIN
                    SELECT RAISE(ABORT, 'valuation_observations is append-only');
                END;
                """
            )
            version = connection.execute(
                "SELECT version FROM accounting_schema WHERE singleton = 1"
            ).fetchone()
            if version is None or int(version[0]) != self.SCHEMA_VERSION:
                raise AccountingPersistenceError("unsupported accounting schema version")

    def create_portfolio(
        self,
        portfolio: VirtualPortfolio,
        opening_event: AccountingEvent,
        opening_transaction: JournalTransaction,
    ) -> None:
        self._validate_linkage(portfolio.portfolio_id, opening_event, opening_transaction)
        if opening_event.sequence != 1:
            raise AccountingPersistenceError("opening event must use sequence 1")
        with self._connect() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    """
                    INSERT INTO virtual_portfolios(portfolio_id, created_at, payload_json)
                    VALUES(?, ?, ?)
                    """,
                    (
                        str(portfolio.portfolio_id),
                        portfolio.created_at.isoformat(),
                        portfolio.model_dump_json(),
                    ),
                )
                self._insert_event(connection, opening_event)
                self._insert_transaction(connection, opening_transaction)
                connection.commit()
            except sqlite3.IntegrityError as exc:
                connection.rollback()
                raise AccountingConflictError("portfolio identity already exists") from exc

    def get_portfolio(self, portfolio_id: UUID) -> VirtualPortfolio:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM virtual_portfolios WHERE portfolio_id = ?",
                (str(portfolio_id),),
            ).fetchone()
        if row is None:
            raise AccountingNotFoundError(f"portfolio {portfolio_id} was not found")
        return VirtualPortfolio.model_validate_json(str(row[0]))

    def list_portfolios(self) -> tuple[VirtualPortfolio, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM virtual_portfolios
                ORDER BY created_at, portfolio_id
                """
            ).fetchall()
        return tuple(VirtualPortfolio.model_validate_json(str(row[0])) for row in rows)

    def next_sequence(self, portfolio_id: UUID) -> int:
        self.get_portfolio(portfolio_id)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COALESCE(MAX(sequence), 0) + 1 FROM accounting_events WHERE portfolio_id = ?",
                (str(portfolio_id),),
            ).fetchone()
        if row is None:
            raise AccountingPersistenceError("failed to allocate accounting sequence")
        return int(row[0])

    def append_event(
        self,
        event: AccountingEvent,
        transaction: JournalTransaction,
    ) -> AccountingEvent:
        self._validate_linkage(event.portfolio_id, event, transaction)
        self.get_portfolio(event.portfolio_id)
        with self._connect() as connection:
            existing = connection.execute(
                """
                SELECT payload_json, content_digest
                FROM accounting_events
                WHERE portfolio_id = ? AND source_kind = ? AND source_id = ?
                """,
                (str(event.portfolio_id), event.source_kind, event.source_id),
            ).fetchone()
            if existing is not None:
                if str(existing[1]) != event.content_digest:
                    raise AccountingConflictError(
                        "accounting source identity already exists with different content"
                    )
                return AccountingEvent.model_validate_json(str(existing[0]))
            try:
                connection.execute("BEGIN IMMEDIATE")
                self._insert_event(connection, event)
                self._insert_transaction(connection, transaction)
                connection.commit()
            except sqlite3.IntegrityError as exc:
                connection.rollback()
                raise AccountingConflictError(
                    "accounting event conflicts with retained immutable evidence"
                ) from exc
        return event

    def get_event(self, event_id: UUID) -> AccountingEvent:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM accounting_events WHERE event_id = ?",
                (str(event_id),),
            ).fetchone()
        if row is None:
            raise AccountingNotFoundError(f"event {event_id} was not found")
        return AccountingEvent.model_validate_json(str(row[0]))

    def list_events(self, portfolio_id: UUID) -> tuple[AccountingEvent, ...]:
        self.get_portfolio(portfolio_id)
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM accounting_events
                WHERE portfolio_id = ?
                ORDER BY sequence
                """,
                (str(portfolio_id),),
            ).fetchall()
        return tuple(AccountingEvent.model_validate_json(str(row[0])) for row in rows)

    def list_transactions(self, portfolio_id: UUID) -> tuple[JournalTransaction, ...]:
        self.get_portfolio(portfolio_id)
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM journal_transactions
                WHERE portfolio_id = ?
                ORDER BY effective_at, transaction_id
                """,
                (str(portfolio_id),),
            ).fetchall()
        return tuple(JournalTransaction.model_validate_json(str(row[0])) for row in rows)

    def append_valuation(
        self,
        observation: ValuationObservation,
    ) -> ValuationObservation:
        self.get_portfolio(observation.portfolio_id)
        payload = observation.model_dump_json()
        with self._connect() as connection:
            existing = connection.execute(
                """
                SELECT payload_json
                FROM valuation_observations
                WHERE portfolio_id = ? AND asset_id = ? AND valuation_revision = ?
                """,
                (
                    str(observation.portfolio_id),
                    observation.asset_id,
                    observation.valuation_revision,
                ),
            ).fetchone()
            if existing is not None:
                retained = ValuationObservation.model_validate_json(str(existing[0]))
                if retained != observation:
                    raise AccountingConflictError(
                        "valuation revision already exists with different content"
                    )
                return retained
            try:
                connection.execute(
                    """
                    INSERT INTO valuation_observations(
                        observation_id,
                        portfolio_id,
                        asset_id,
                        valuation_revision,
                        price_effective_at,
                        payload_json
                    ) VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(observation.observation_id),
                        str(observation.portfolio_id),
                        observation.asset_id,
                        observation.valuation_revision,
                        observation.price_effective_at.isoformat(),
                        payload,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise AccountingConflictError(
                    "valuation observation conflicts with retained immutable evidence"
                ) from exc
        return observation

    def list_valuations(self, portfolio_id: UUID) -> tuple[ValuationObservation, ...]:
        self.get_portfolio(portfolio_id)
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM valuation_observations
                WHERE portfolio_id = ?
                ORDER BY price_effective_at, observation_id
                """,
                (str(portfolio_id),),
            ).fetchall()
        return tuple(ValuationObservation.model_validate_json(str(row[0])) for row in rows)

    @staticmethod
    def _validate_linkage(
        portfolio_id: UUID,
        event: AccountingEvent,
        transaction: JournalTransaction,
    ) -> None:
        if event.portfolio_id != portfolio_id:
            raise AccountingPersistenceError("event portfolio linkage does not match")
        if transaction.portfolio_id != portfolio_id or transaction.event_id != event.event_id:
            raise AccountingPersistenceError("journal transaction linkage does not match event")

    @staticmethod
    def _insert_event(connection: sqlite3.Connection, event: AccountingEvent) -> None:
        connection.execute(
            """
            INSERT INTO accounting_events(
                event_id,
                portfolio_id,
                sequence,
                event_type,
                source_kind,
                source_id,
                content_digest,
                effective_at,
                payload_json
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(event.event_id),
                str(event.portfolio_id),
                event.sequence,
                event.event_type.value,
                event.source_kind,
                event.source_id,
                event.content_digest,
                event.effective_at.isoformat(),
                event.model_dump_json(),
            ),
        )

    @staticmethod
    def _insert_transaction(
        connection: sqlite3.Connection,
        transaction: JournalTransaction,
    ) -> None:
        connection.execute(
            """
            INSERT INTO journal_transactions(
                transaction_id,
                portfolio_id,
                event_id,
                effective_at,
                payload_json
            ) VALUES(?, ?, ?, ?, ?)
            """,
            (
                str(transaction.transaction_id),
                str(transaction.portfolio_id),
                str(transaction.event_id),
                transaction.effective_at.isoformat(),
                transaction.model_dump_json(),
            ),
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
