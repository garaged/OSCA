import sqlite3
from pathlib import Path
from typing import cast
from uuid import UUID

from osca.backtesting.eventing.contracts import (
    JournalTransaction,
    OrderLifecycleEvent,
    PortfolioProjection,
    PromotionGateDecision,
    SimulatedFill,
    ValuationSnapshot,
)

_SCHEMA_VERSION = 1


class SQLiteF2ValidationStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS f2_validation_store_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS f2_validation_records (
                    record_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    record_type TEXT NOT NULL,
                    effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_f2_validation_records_request
                    ON f2_validation_records(request_id, effective_at, record_id);

                CREATE INDEX IF NOT EXISTS idx_f2_validation_records_type
                    ON f2_validation_records(record_type, request_id, effective_at);
                """
            )
            connection.execute(
                """
                INSERT INTO f2_validation_store_metadata(key, value)
                VALUES ('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(_SCHEMA_VERSION),),
            )

    def save_order_lifecycle_event(self, event: OrderLifecycleEvent) -> None:
        self._save_record(
            record_id=event.lifecycle_event_id,
            request_id=event.request_id,
            record_type="order_lifecycle",
            effective_at=event.effective_at.isoformat(),
            payload_json=event.model_dump_json(),
        )

    def list_order_lifecycle_events(self, request_id: UUID) -> tuple[OrderLifecycleEvent, ...]:
        return tuple(
            OrderLifecycleEvent.model_validate_json(payload)
            for payload in self._list_payloads(request_id, "order_lifecycle")
        )

    def save_fill(self, fill: SimulatedFill) -> None:
        self._save_record(
            record_id=fill.fill_id,
            request_id=fill.request_id,
            record_type="fill",
            effective_at=fill.effective_at.isoformat(),
            payload_json=fill.model_dump_json(),
        )

    def list_fills(self, request_id: UUID) -> tuple[SimulatedFill, ...]:
        return tuple(
            SimulatedFill.model_validate_json(payload)
            for payload in self._list_payloads(request_id, "fill")
        )

    def save_journal_transaction(self, transaction: JournalTransaction) -> None:
        self._save_record(
            record_id=transaction.transaction_id,
            request_id=transaction.request_id,
            record_type="journal_transaction",
            effective_at=transaction.effective_at.isoformat(),
            payload_json=transaction.model_dump_json(),
        )

    def list_journal_transactions(self, request_id: UUID) -> tuple[JournalTransaction, ...]:
        return tuple(
            JournalTransaction.model_validate_json(payload)
            for payload in self._list_payloads(request_id, "journal_transaction")
        )

    def save_valuation_snapshot(self, snapshot: ValuationSnapshot) -> None:
        self._save_record(
            record_id=snapshot.valuation_id,
            request_id=snapshot.request_id,
            record_type="valuation",
            effective_at=snapshot.effective_at.isoformat(),
            payload_json=snapshot.model_dump_json(),
        )

    def list_valuation_snapshots(self, request_id: UUID) -> tuple[ValuationSnapshot, ...]:
        return tuple(
            ValuationSnapshot.model_validate_json(payload)
            for payload in self._list_payloads(request_id, "valuation")
        )

    def save_projection(self, projection: PortfolioProjection) -> None:
        self._save_record(
            record_id=projection.projection_id,
            request_id=projection.request_id,
            record_type="portfolio_projection",
            effective_at=projection.generated_at.isoformat(),
            payload_json=projection.model_dump_json(),
        )

    def list_projections(self, request_id: UUID) -> tuple[PortfolioProjection, ...]:
        return tuple(
            PortfolioProjection.model_validate_json(payload)
            for payload in self._list_payloads(request_id, "portfolio_projection")
        )

    def save_promotion_gate(self, gate: PromotionGateDecision) -> None:
        self._save_record(
            record_id=gate.gate_id,
            request_id=gate.request_id,
            record_type="promotion_gate",
            effective_at=gate.decided_at.isoformat(),
            payload_json=gate.model_dump_json(),
        )

    def list_promotion_gates(self, request_id: UUID) -> tuple[PromotionGateDecision, ...]:
        return tuple(
            PromotionGateDecision.model_validate_json(payload)
            for payload in self._list_payloads(request_id, "promotion_gate")
        )

    def _save_record(
        self,
        *,
        record_id: UUID,
        request_id: UUID,
        record_type: str,
        effective_at: str,
        payload_json: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO f2_validation_records(
                    record_id,
                    request_id,
                    record_type,
                    effective_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET
                    request_id = excluded.request_id,
                    record_type = excluded.record_type,
                    effective_at = excluded.effective_at,
                    payload_json = excluded.payload_json
                """,
                (str(record_id), str(request_id), record_type, effective_at, payload_json),
            )

    def _list_payloads(self, request_id: UUID, record_type: str) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM f2_validation_records
                WHERE request_id = ? AND record_type = ?
                ORDER BY effective_at, record_id
                """,
                (str(request_id), record_type),
            ).fetchall()
        return tuple(cast(str, row["payload_json"]) for row in rows)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection
