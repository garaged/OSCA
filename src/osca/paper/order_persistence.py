"""Append-only SQLite persistence for D9 simulated order authority."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import UUID

from pydantic import BaseModel

from osca.paper.contracts import PaperRunCheckpoint
from osca.paper.order_contracts import (
    ExecutionAssumptions,
    OrderLifecycleEvent,
    PaperRiskDecision,
    PaperRunBinding,
    SimulatedFill,
    SimulatedOrder,
    SimulatedOrderConfirmation,
    SimulatedOrderDraft,
)


class OrderPersistenceError(RuntimeError):
    """Base error for D9 order persistence failures."""


class OrderConflictError(OrderPersistenceError):
    """Raised when immutable identities conflict with retained evidence."""


class OrderNotFoundError(OrderPersistenceError):
    """Raised when requested D9 order evidence does not exist."""


class SQLitePaperOrderStore:
    """Profile-scoped append-only store for D9 paper order evidence."""

    SCHEMA_VERSION = 1

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS paper_order_schema (
                    singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                    version INTEGER NOT NULL
                );
                INSERT OR IGNORE INTO paper_order_schema(singleton, version) VALUES(1, 1);

                CREATE TABLE IF NOT EXISTS paper_run_bindings (
                    binding_id TEXT PRIMARY KEY,
                    paper_run_id TEXT NOT NULL UNIQUE,
                    paper_account_id TEXT NOT NULL,
                    portfolio_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS execution_assumptions (
                    assumption_id TEXT PRIMARY KEY,
                    revision INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS simulated_order_drafts (
                    draft_id TEXT NOT NULL,
                    draft_version INTEGER NOT NULL,
                    paper_run_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY(draft_id, draft_version)
                );

                CREATE TABLE IF NOT EXISTS simulated_order_confirmations (
                    confirmation_id TEXT PRIMARY KEY,
                    draft_id TEXT NOT NULL,
                    draft_version INTEGER NOT NULL,
                    confirmed_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    UNIQUE(draft_id, draft_version)
                );

                CREATE TABLE IF NOT EXISTS simulated_orders (
                    order_id TEXT PRIMARY KEY,
                    confirmation_id TEXT NOT NULL UNIQUE,
                    paper_run_id TEXT NOT NULL,
                    portfolio_id TEXT NOT NULL,
                    eligible_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS order_lifecycle_events (
                    event_id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    source_id TEXT NOT NULL,
                    effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    UNIQUE(order_id, sequence),
                    UNIQUE(order_id, source_id)
                );

                CREATE TABLE IF NOT EXISTS simulated_fills (
                    fill_id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    source_id TEXT NOT NULL,
                    bar_evidence_id TEXT NOT NULL,
                    effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    UNIQUE(order_id, sequence),
                    UNIQUE(order_id, source_id),
                    UNIQUE(order_id, bar_evidence_id)
                );

                CREATE TABLE IF NOT EXISTS paper_risk_decisions (
                    risk_decision_id TEXT PRIMARY KEY,
                    order_id TEXT NOT NULL,
                    checked_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS forward_checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    paper_run_id TEXT NOT NULL,
                    sequence_number INTEGER NOT NULL,
                    idempotency_key TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    UNIQUE(paper_run_id, sequence_number),
                    UNIQUE(paper_run_id, idempotency_key)
                );

                CREATE INDEX IF NOT EXISTS idx_order_drafts_run
                    ON simulated_order_drafts(paper_run_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_orders_run
                    ON simulated_orders(paper_run_id, eligible_at);
                CREATE INDEX IF NOT EXISTS idx_lifecycle_order_sequence
                    ON order_lifecycle_events(order_id, sequence);
                CREATE INDEX IF NOT EXISTS idx_fills_order_sequence
                    ON simulated_fills(order_id, sequence);
                CREATE INDEX IF NOT EXISTS idx_checkpoints_run_sequence
                    ON forward_checkpoints(paper_run_id, sequence_number);
                """
            )
            for table in self._append_only_tables():
                self._install_append_only_triggers(connection, table)
            row = connection.execute(
                "SELECT version FROM paper_order_schema WHERE singleton = 1"
            ).fetchone()
            if row is None or int(row[0]) != self.SCHEMA_VERSION:
                raise OrderPersistenceError("unsupported paper order schema version")

    def append_binding(self, binding: PaperRunBinding) -> PaperRunBinding:
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT payload_json FROM paper_run_bindings WHERE paper_run_id = ?",
                (str(binding.paper_run_id),),
            ).fetchone()
            if existing is not None:
                retained = PaperRunBinding.model_validate_json(str(existing[0]))
                self._require_same(retained, binding, "paper run binding")
                return retained
            self._execute_insert(
                connection,
                """
                INSERT INTO paper_run_bindings(
                    binding_id, paper_run_id, paper_account_id, portfolio_id,
                    created_at, payload_json
                ) VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    str(binding.binding_id),
                    str(binding.paper_run_id),
                    str(binding.paper_account_id),
                    str(binding.portfolio_id),
                    binding.created_at.isoformat(),
                    binding.model_dump_json(),
                ),
                "paper run binding",
            )
        return binding

    def get_binding(self, paper_run_id: UUID) -> PaperRunBinding:
        return self._get_one(
            "paper_run_bindings",
            "paper_run_id",
            str(paper_run_id),
            PaperRunBinding,
            "paper run binding",
        )

    def append_assumptions(self, assumptions: ExecutionAssumptions) -> ExecutionAssumptions:
        return self._append_identity_payload(
            table="execution_assumptions",
            identity_column="assumption_id",
            identity=str(assumptions.assumption_id),
            columns=("assumption_id", "revision", "created_at", "payload_json"),
            values=(
                str(assumptions.assumption_id),
                assumptions.revision,
                assumptions.created_at.isoformat(),
                assumptions.model_dump_json(),
            ),
            model=ExecutionAssumptions,
            value=assumptions,
            label="execution assumptions",
        )

    def get_assumptions(self, assumption_id: UUID) -> ExecutionAssumptions:
        return self._get_one(
            "execution_assumptions",
            "assumption_id",
            str(assumption_id),
            ExecutionAssumptions,
            "execution assumptions",
        )

    def append_draft(self, draft: SimulatedOrderDraft) -> SimulatedOrderDraft:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json FROM simulated_order_drafts
                WHERE draft_id = ? AND draft_version = ?
                """,
                (str(draft.draft_id), draft.draft_version),
            ).fetchone()
            if row is not None:
                retained = SimulatedOrderDraft.model_validate_json(str(row[0]))
                self._require_same(retained, draft, "simulated order draft")
                return retained
            self._execute_insert(
                connection,
                """
                INSERT INTO simulated_order_drafts(
                    draft_id, draft_version, paper_run_id, created_at, payload_json
                ) VALUES(?, ?, ?, ?, ?)
                """,
                (
                    str(draft.draft_id),
                    draft.draft_version,
                    str(draft.paper_run_id),
                    draft.created_at.isoformat(),
                    draft.model_dump_json(),
                ),
                "simulated order draft",
            )
        return draft

    def list_drafts(self, paper_run_id: UUID) -> tuple[SimulatedOrderDraft, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json FROM simulated_order_drafts
                WHERE paper_run_id = ? ORDER BY created_at, draft_id, draft_version
                """,
                (str(paper_run_id),),
            ).fetchall()
        return tuple(SimulatedOrderDraft.model_validate_json(str(row[0])) for row in rows)

    def append_confirmation_and_order(
        self,
        confirmation: SimulatedOrderConfirmation,
        order: SimulatedOrder,
    ) -> tuple[SimulatedOrderConfirmation, SimulatedOrder]:
        if confirmation.confirmation_id != order.confirmation_id:
            raise OrderPersistenceError("confirmation and order identities do not match")
        if confirmation.draft_id != order.draft_id:
            raise OrderPersistenceError("confirmation and order draft identities do not match")
        with self._connect() as connection:
            existing = connection.execute(
                """
                SELECT c.payload_json, o.payload_json
                FROM simulated_order_confirmations c
                JOIN simulated_orders o ON o.confirmation_id = c.confirmation_id
                WHERE c.draft_id = ? AND c.draft_version = ?
                """,
                (str(confirmation.draft_id), confirmation.draft_version),
            ).fetchone()
            if existing is not None:
                retained_confirmation = SimulatedOrderConfirmation.model_validate_json(
                    str(existing[0])
                )
                retained_order = SimulatedOrder.model_validate_json(str(existing[1]))
                self._require_same(retained_confirmation, confirmation, "order confirmation")
                self._require_same(retained_order, order, "simulated order")
                return retained_confirmation, retained_order
            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    """
                    INSERT INTO simulated_order_confirmations(
                        confirmation_id, draft_id, draft_version, confirmed_at, payload_json
                    ) VALUES(?, ?, ?, ?, ?)
                    """,
                    (
                        str(confirmation.confirmation_id),
                        str(confirmation.draft_id),
                        confirmation.draft_version,
                        confirmation.confirmed_at.isoformat(),
                        confirmation.model_dump_json(),
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO simulated_orders(
                        order_id, confirmation_id, paper_run_id, portfolio_id,
                        eligible_at, payload_json
                    ) VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(order.order_id),
                        str(order.confirmation_id),
                        str(order.paper_run_id),
                        str(order.portfolio_id),
                        order.eligible_at.isoformat(),
                        order.model_dump_json(),
                    ),
                )
                connection.commit()
            except sqlite3.IntegrityError as exc:
                connection.rollback()
                raise OrderConflictError(
                    "confirmation/order conflicts with retained evidence"
                ) from exc
        return confirmation, order

    def get_order(self, order_id: UUID) -> SimulatedOrder:
        return self._get_one(
            "simulated_orders",
            "order_id",
            str(order_id),
            SimulatedOrder,
            "simulated order",
        )

    def list_orders(self, paper_run_id: UUID) -> tuple[SimulatedOrder, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json FROM simulated_orders
                WHERE paper_run_id = ? ORDER BY eligible_at, order_id
                """,
                (str(paper_run_id),),
            ).fetchall()
        return tuple(SimulatedOrder.model_validate_json(str(row[0])) for row in rows)

    def next_lifecycle_sequence(self, order_id: UUID) -> int:
        self.get_order(order_id)
        return self._next_sequence("order_lifecycle_events", "order_id", str(order_id))

    def append_lifecycle(self, event: OrderLifecycleEvent) -> OrderLifecycleEvent:
        self.get_order(event.order_id)
        return self._append_identity_payload(
            table="order_lifecycle_events",
            identity_column="source_id",
            identity=event.source_id,
            scope=("order_id", str(event.order_id)),
            columns=(
                "event_id",
                "order_id",
                "sequence",
                "source_id",
                "effective_at",
                "payload_json",
            ),
            values=(
                str(event.event_id),
                str(event.order_id),
                event.sequence,
                event.source_id,
                event.effective_at.isoformat(),
                event.model_dump_json(),
            ),
            model=OrderLifecycleEvent,
            value=event,
            label="order lifecycle event",
        )

    def list_lifecycle(self, order_id: UUID) -> tuple[OrderLifecycleEvent, ...]:
        self.get_order(order_id)
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json FROM order_lifecycle_events
                WHERE order_id = ? ORDER BY sequence
                """,
                (str(order_id),),
            ).fetchall()
        return tuple(OrderLifecycleEvent.model_validate_json(str(row[0])) for row in rows)

    def next_fill_sequence(self, order_id: UUID) -> int:
        self.get_order(order_id)
        return self._next_sequence("simulated_fills", "order_id", str(order_id))

    def append_fill(self, fill: SimulatedFill) -> SimulatedFill:
        self.get_order(fill.order_id)
        return self._append_identity_payload(
            table="simulated_fills",
            identity_column="source_id",
            identity=fill.source_id,
            scope=("order_id", str(fill.order_id)),
            columns=(
                "fill_id",
                "order_id",
                "sequence",
                "source_id",
                "bar_evidence_id",
                "effective_at",
                "payload_json",
            ),
            values=(
                str(fill.fill_id),
                str(fill.order_id),
                fill.sequence,
                fill.source_id,
                str(fill.bar_evidence_id),
                fill.effective_at.isoformat(),
                fill.model_dump_json(),
            ),
            model=SimulatedFill,
            value=fill,
            label="simulated fill",
        )

    def list_fills(self, order_id: UUID) -> tuple[SimulatedFill, ...]:
        self.get_order(order_id)
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload_json FROM simulated_fills WHERE order_id = ? ORDER BY sequence",
                (str(order_id),),
            ).fetchall()
        return tuple(SimulatedFill.model_validate_json(str(row[0])) for row in rows)

    def append_risk_decision(self, decision: PaperRiskDecision) -> PaperRiskDecision:
        self.get_order(decision.order_id)
        return self._append_identity_payload(
            table="paper_risk_decisions",
            identity_column="risk_decision_id",
            identity=str(decision.risk_decision_id),
            columns=("risk_decision_id", "order_id", "checked_at", "payload_json"),
            values=(
                str(decision.risk_decision_id),
                str(decision.order_id),
                decision.checked_at.isoformat(),
                decision.model_dump_json(),
            ),
            model=PaperRiskDecision,
            value=decision,
            label="paper risk decision",
        )

    def append_checkpoint(self, checkpoint: PaperRunCheckpoint) -> PaperRunCheckpoint:
        return self._append_identity_payload(
            table="forward_checkpoints",
            identity_column="idempotency_key",
            identity=checkpoint.idempotency_key,
            scope=("paper_run_id", str(checkpoint.paper_run_id)),
            columns=(
                "checkpoint_id",
                "paper_run_id",
                "sequence_number",
                "idempotency_key",
                "created_at",
                "payload_json",
            ),
            values=(
                str(checkpoint.checkpoint_id),
                str(checkpoint.paper_run_id),
                checkpoint.sequence_number,
                checkpoint.idempotency_key,
                checkpoint.created_at.isoformat(),
                checkpoint.model_dump_json(),
            ),
            model=PaperRunCheckpoint,
            value=checkpoint,
            label="forward checkpoint",
        )

    def get_checkpoint_by_key(
        self,
        paper_run_id: UUID,
        idempotency_key: str,
    ) -> PaperRunCheckpoint | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json FROM forward_checkpoints
                WHERE paper_run_id = ? AND idempotency_key = ?
                """,
                (str(paper_run_id), idempotency_key),
            ).fetchone()
        if row is None:
            return None
        return PaperRunCheckpoint.model_validate_json(str(row[0]))

    def latest_checkpoint(self, paper_run_id: UUID) -> PaperRunCheckpoint | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json FROM forward_checkpoints
                WHERE paper_run_id = ? ORDER BY sequence_number DESC LIMIT 1
                """,
                (str(paper_run_id),),
            ).fetchone()
        if row is None:
            return None
        return PaperRunCheckpoint.model_validate_json(str(row[0]))

    def _append_identity_payload[ModelT: BaseModel](
        self,
        *,
        table: str,
        identity_column: str,
        identity: str,
        columns: tuple[str, ...],
        values: tuple[object, ...],
        model: type[ModelT],
        value: ModelT,
        label: str,
        scope: tuple[str, str] | None = None,
    ) -> ModelT:
        where = f"{identity_column} = ?"
        parameters: list[object] = [identity]
        if scope is not None:
            where += f" AND {scope[0]} = ?"
            parameters.append(scope[1])
        with self._connect() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} WHERE {where}",
                tuple(parameters),
            ).fetchone()
            if row is not None:
                retained = model.model_validate_json(str(row[0]))
                self._require_same(retained, value, label)
                return retained
            placeholders = ", ".join("?" for _ in columns)
            column_sql = ", ".join(columns)
            self._execute_insert(
                connection,
                f"INSERT INTO {table}({column_sql}) VALUES({placeholders})",
                values,
                label,
            )
        return value

    def _get_one[ModelT: BaseModel](
        self,
        table: str,
        identity_column: str,
        identity: str,
        model: type[ModelT],
        label: str,
    ) -> ModelT:
        with self._connect() as connection:
            row = connection.execute(
                f"SELECT payload_json FROM {table} WHERE {identity_column} = ?",
                (identity,),
            ).fetchone()
        if row is None:
            raise OrderNotFoundError(f"{label} {identity} was not found")
        return model.model_validate_json(str(row[0]))

    def _next_sequence(self, table: str, scope_column: str, scope_id: str) -> int:
        with self._connect() as connection:
            row = connection.execute(
                f"SELECT COALESCE(MAX(sequence), 0) + 1 FROM {table} "
                f"WHERE {scope_column} = ?",
                (scope_id,),
            ).fetchone()
        if row is None:
            raise OrderPersistenceError("failed to allocate append-only sequence")
        return int(row[0])

    @staticmethod
    def _execute_insert(
        connection: sqlite3.Connection,
        sql: str,
        values: tuple[object, ...],
        label: str,
    ) -> None:
        try:
            connection.execute(sql, values)
        except sqlite3.IntegrityError as exc:
            raise OrderConflictError(f"{label} conflicts with retained evidence") from exc

    @staticmethod
    def _require_same(retained: object, candidate: object, label: str) -> None:
        if retained != candidate:
            raise OrderConflictError(f"{label} identity already exists with different content")

    @staticmethod
    def _append_only_tables() -> tuple[str, ...]:
        return (
            "paper_run_bindings",
            "execution_assumptions",
            "simulated_order_drafts",
            "simulated_order_confirmations",
            "simulated_orders",
            "order_lifecycle_events",
            "simulated_fills",
            "paper_risk_decisions",
            "forward_checkpoints",
        )

    @staticmethod
    def _install_append_only_triggers(connection: sqlite3.Connection, table: str) -> None:
        connection.executescript(
            f"""
            CREATE TRIGGER IF NOT EXISTS {table}_no_update
            BEFORE UPDATE ON {table} BEGIN
                SELECT RAISE(ABORT, '{table} is append-only');
            END;
            CREATE TRIGGER IF NOT EXISTS {table}_no_delete
            BEFORE DELETE ON {table} BEGIN
                SELECT RAISE(ABORT, '{table} is append-only');
            END;
            """
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection