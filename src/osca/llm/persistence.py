import sqlite3
from pathlib import Path

from osca.llm.contracts import (
    LLMEvaluationReport,
    LLMProviderCapability,
    LLMPromptTemplate,
    LLMRequestEnvelope,
    LLMRouteDecision,
)

_SCHEMA_VERSION = 1


class SQLiteLLMLifecycleStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS llm_store_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS llm_records (
                    record_id TEXT PRIMARY KEY,
                    provider_id TEXT,
                    request_id TEXT,
                    route_decision_id TEXT,
                    record_type TEXT NOT NULL,
                    effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_llm_records_provider
                    ON llm_records(provider_id, record_type, effective_at, record_id);

                CREATE INDEX IF NOT EXISTS idx_llm_records_request
                    ON llm_records(request_id, record_type, effective_at, record_id);

                CREATE INDEX IF NOT EXISTS idx_llm_records_route
                    ON llm_records(route_decision_id, record_type, effective_at, record_id);
                """
            )
            connection.execute(
                """
                INSERT INTO llm_store_metadata(key, value)
                VALUES ('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(_SCHEMA_VERSION),),
            )

    def save_provider_capability(self, capability: LLMProviderCapability) -> None:
        self._save_record(
            record_id=f"{capability.provider_id}:{capability.model_id}:{capability.model_version}",
            provider_id=capability.provider_id,
            request_id=None,
            route_decision_id=None,
            record_type="provider_capability",
            effective_at=capability.declared_at.isoformat(),
            payload_json=capability.model_dump_json(),
        )

    def list_provider_capabilities(self) -> tuple[LLMProviderCapability, ...]:
        return tuple(
            LLMProviderCapability.model_validate_json(payload)
            for payload in self._list_payloads_by_type("provider_capability")
        )

    def save_prompt_template(self, prompt: LLMPromptTemplate) -> None:
        self._save_record(
            record_id=f"{prompt.prompt_id}:{prompt.prompt_version}",
            provider_id=None,
            request_id=None,
            route_decision_id=None,
            record_type="prompt_template",
            effective_at=prompt.created_at.isoformat(),
            payload_json=prompt.model_dump_json(),
        )

    def list_prompt_templates(self) -> tuple[LLMPromptTemplate, ...]:
        return tuple(
            LLMPromptTemplate.model_validate_json(payload)
            for payload in self._list_payloads_by_type("prompt_template")
        )

    def save_request(self, request: LLMRequestEnvelope) -> None:
        self._save_record(
            record_id=request.request_id,
            provider_id=None,
            request_id=request.request_id,
            route_decision_id=None,
            record_type="request",
            effective_at=request.requested_at.isoformat(),
            payload_json=request.model_dump_json(),
        )

    def list_requests(self) -> tuple[LLMRequestEnvelope, ...]:
        return tuple(
            LLMRequestEnvelope.model_validate_json(payload)
            for payload in self._list_payloads_by_type("request")
        )

    def save_route_decision(self, decision: LLMRouteDecision) -> None:
        self._save_record(
            record_id=decision.route_decision_id,
            provider_id=decision.provider_id,
            request_id=decision.request_id,
            route_decision_id=decision.route_decision_id,
            record_type="route_decision",
            effective_at=decision.decided_at.isoformat(),
            payload_json=decision.model_dump_json(),
        )

    def list_route_decisions(self, request_id: str) -> tuple[LLMRouteDecision, ...]:
        return tuple(
            LLMRouteDecision.model_validate_json(payload)
            for payload in self._list_payloads_by_request(request_id, "route_decision")
        )

    def save_evaluation_report(self, report: LLMEvaluationReport) -> None:
        self._save_record(
            record_id=report.evaluation_report_id,
            provider_id=None,
            request_id=report.request_id,
            route_decision_id=report.route_decision_id,
            record_type="evaluation_report",
            effective_at=report.evaluated_at.isoformat(),
            payload_json=report.model_dump_json(),
        )

    def list_evaluation_reports(self, request_id: str) -> tuple[LLMEvaluationReport, ...]:
        return tuple(
            LLMEvaluationReport.model_validate_json(payload)
            for payload in self._list_payloads_by_request(request_id, "evaluation_report")
        )

    def _save_record(
        self,
        *,
        record_id: object,
        provider_id: object | None,
        request_id: object | None,
        route_decision_id: object | None,
        record_type: str,
        effective_at: str,
        payload_json: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO llm_records(
                    record_id,
                    provider_id,
                    request_id,
                    route_decision_id,
                    record_type,
                    effective_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET
                    provider_id = excluded.provider_id,
                    request_id = excluded.request_id,
                    route_decision_id = excluded.route_decision_id,
                    record_type = excluded.record_type,
                    effective_at = excluded.effective_at,
                    payload_json = excluded.payload_json
                """,
                (
                    str(record_id),
                    None if provider_id is None else str(provider_id),
                    None if request_id is None else str(request_id),
                    None if route_decision_id is None else str(route_decision_id),
                    record_type,
                    effective_at,
                    payload_json,
                ),
            )

    def _list_payloads_by_type(self, record_type: str) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM llm_records
                WHERE record_type = ?
                ORDER BY effective_at, record_id
                """,
                (record_type,),
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def _list_payloads_by_request(self, request_id: str, record_type: str) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM llm_records
                WHERE request_id = ? AND record_type = ?
                ORDER BY effective_at, record_id
                """,
                (request_id, record_type),
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)
