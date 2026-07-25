import sqlite3
from pathlib import Path
from typing import cast
from uuid import UUID

from osca.backtesting.api import (
    BacktestExecutionPlan,
    BacktestRequest,
    BacktestResult,
)

_SCHEMA_VERSION = 1


class SQLiteBacktestLifecycleStore:
    """SQLite store for backtest request, execution-plan, and result records."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS backtest_store_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS backtest_requests (
                    request_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    strategy_id TEXT NOT NULL,
                    fidelity_profile TEXT NOT NULL,
                    execution_mode TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_backtest_requests_project
                    ON backtest_requests(project_id, created_at);

                CREATE INDEX IF NOT EXISTS idx_backtest_requests_strategy
                    ON backtest_requests(strategy_id, created_at);

                CREATE TABLE IF NOT EXISTS backtest_execution_plans (
                    request_id TEXT PRIMARY KEY,
                    can_execute INTEGER NOT NULL,
                    planned_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    FOREIGN KEY (request_id)
                        REFERENCES backtest_requests(request_id)
                        ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS backtest_results (
                    result_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    FOREIGN KEY (request_id)
                        REFERENCES backtest_requests(request_id)
                        ON DELETE RESTRICT
                );

                CREATE INDEX IF NOT EXISTS idx_backtest_results_request
                    ON backtest_results(request_id, generated_at);
                """
            )
            connection.execute(
                """
                INSERT INTO backtest_store_metadata(key, value)
                VALUES ('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(_SCHEMA_VERSION),),
            )

    def save_request(self, request: BacktestRequest) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO backtest_requests(
                    request_id,
                    project_id,
                    strategy_id,
                    fidelity_profile,
                    execution_mode,
                    created_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(request_id) DO UPDATE SET
                    project_id = excluded.project_id,
                    strategy_id = excluded.strategy_id,
                    fidelity_profile = excluded.fidelity_profile,
                    execution_mode = excluded.execution_mode,
                    created_at = excluded.created_at,
                    payload_json = excluded.payload_json
                """,
                (
                    str(request.request_id),
                    str(request.project_id),
                    request.strategy_id,
                    request.fidelity_profile.value,
                    request.execution_mode.value,
                    request.created_at.isoformat(),
                    request.model_dump_json(),
                ),
            )

    def get_request(self, request_id: UUID) -> BacktestRequest | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json
                FROM backtest_requests
                WHERE request_id = ?
                """,
                (str(request_id),),
            ).fetchone()
        if row is None:
            return None
        return BacktestRequest.model_validate_json(cast(str, row["payload_json"]))

    def list_requests(
        self, *, project_id: UUID | None = None, strategy_id: str | None = None
    ) -> tuple[BacktestRequest, ...]:
        filters: list[str] = []
        parameters: list[str] = []
        if project_id is not None:
            filters.append("project_id = ?")
            parameters.append(str(project_id))
        if strategy_id is not None:
            filters.append("strategy_id = ?")
            parameters.append(strategy_id)

        query = "SELECT payload_json FROM backtest_requests"
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY created_at, request_id"

        with self._connect() as connection:
            rows = connection.execute(query, tuple(parameters)).fetchall()
        return tuple(
            BacktestRequest.model_validate_json(cast(str, row["payload_json"]))
            for row in rows
        )

    def save_execution_plan(self, plan: BacktestExecutionPlan) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO backtest_execution_plans(
                    request_id,
                    can_execute,
                    planned_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(request_id) DO UPDATE SET
                    can_execute = excluded.can_execute,
                    planned_at = excluded.planned_at,
                    payload_json = excluded.payload_json
                """,
                (
                    str(plan.request_id),
                    int(plan.can_execute),
                    plan.planned_at.isoformat(),
                    plan.model_dump_json(),
                ),
            )

    def get_execution_plan(self, request_id: UUID) -> BacktestExecutionPlan | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json
                FROM backtest_execution_plans
                WHERE request_id = ?
                """,
                (str(request_id),),
            ).fetchone()
        if row is None:
            return None
        return BacktestExecutionPlan.model_validate_json(cast(str, row["payload_json"]))

    def save_result(self, result: BacktestResult) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO backtest_results(
                    result_id,
                    request_id,
                    status,
                    generated_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(result_id) DO UPDATE SET
                    request_id = excluded.request_id,
                    status = excluded.status,
                    generated_at = excluded.generated_at,
                    payload_json = excluded.payload_json
                """,
                (
                    str(result.result_id),
                    str(result.request_id),
                    result.status.value,
                    result.generated_at.isoformat(),
                    result.model_dump_json(),
                ),
            )

    def get_result(self, result_id: UUID) -> BacktestResult | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json
                FROM backtest_results
                WHERE result_id = ?
                """,
                (str(result_id),),
            ).fetchone()
        if row is None:
            return None
        return BacktestResult.model_validate_json(cast(str, row["payload_json"]))

    def list_results_for_request(self, request_id: UUID) -> tuple[BacktestResult, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM backtest_results
                WHERE request_id = ?
                ORDER BY generated_at, result_id
                """,
                (str(request_id),),
            ).fetchall()
        return tuple(
            BacktestResult.model_validate_json(cast(str, row["payload_json"]))
            for row in rows
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
