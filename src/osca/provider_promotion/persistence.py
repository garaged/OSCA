import sqlite3
from pathlib import Path

from osca.provider_promotion.contracts import (
    ProviderIdentifier,
    ProviderProductionEvidenceBundle,
    ProviderPromotionDecision,
)

_SCHEMA_VERSION = 1


class SQLiteProviderPromotionStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS provider_promotion_store_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS provider_promotion_records (
                    record_id TEXT PRIMARY KEY,
                    provider_id TEXT NOT NULL,
                    record_type TEXT NOT NULL,
                    effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_provider_promotion_provider
                    ON provider_promotion_records(provider_id, record_type, effective_at);
                """
            )
            connection.execute(
                """
                INSERT INTO provider_promotion_store_metadata(key, value)
                VALUES ('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(_SCHEMA_VERSION),),
            )

    def save_evidence_bundle(self, evidence: ProviderProductionEvidenceBundle) -> None:
        self._save_record(
            record_id=str(evidence.evidence_bundle_id),
            provider_id=evidence.provider_id,
            record_type="evidence_bundle",
            effective_at=evidence.reviewed_at.isoformat(),
            payload_json=evidence.model_dump_json(),
        )

    def list_evidence_bundles(
        self,
        provider_id: ProviderIdentifier,
    ) -> tuple[ProviderProductionEvidenceBundle, ...]:
        return tuple(
            ProviderProductionEvidenceBundle.model_validate_json(payload)
            for payload in self._list_payloads(provider_id, "evidence_bundle")
        )

    def save_promotion_decision(self, decision: ProviderPromotionDecision) -> None:
        self._save_record(
            record_id=str(decision.promotion_decision_id),
            provider_id=decision.provider_id,
            record_type="promotion_decision",
            effective_at=decision.decided_at.isoformat(),
            payload_json=decision.model_dump_json(),
        )

    def list_promotion_decisions(
        self,
        provider_id: ProviderIdentifier,
    ) -> tuple[ProviderPromotionDecision, ...]:
        return tuple(
            ProviderPromotionDecision.model_validate_json(payload)
            for payload in self._list_payloads(provider_id, "promotion_decision")
        )

    def _save_record(
        self,
        *,
        record_id: str,
        provider_id: ProviderIdentifier,
        record_type: str,
        effective_at: str,
        payload_json: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO provider_promotion_records(
                    record_id,
                    provider_id,
                    record_type,
                    effective_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET
                    provider_id = excluded.provider_id,
                    record_type = excluded.record_type,
                    effective_at = excluded.effective_at,
                    payload_json = excluded.payload_json
                """,
                (
                    record_id,
                    provider_id.value,
                    record_type,
                    effective_at,
                    payload_json,
                ),
            )

    def _list_payloads(
        self,
        provider_id: ProviderIdentifier,
        record_type: str,
    ) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM provider_promotion_records
                WHERE provider_id = ? AND record_type = ?
                ORDER BY effective_at, record_id
                """,
                (provider_id.value, record_type),
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)
