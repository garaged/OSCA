import sqlite3
from pathlib import Path
from typing import cast
from uuid import UUID

from osca.paper.contracts import (
    ApprovedPaperCandidate,
    ForwardComparisonRecord,
    PaperAccount,
    PaperControlDecision,
    PaperEvaluationRequest,
    PaperHealthGateDecision,
    PaperRecoveryDecision,
    PaperRunCheckpoint,
    PaperSchedule,
)

_SCHEMA_VERSION = 1


class SQLitePaperEvaluationStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS paper_store_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS paper_records (
                    record_id TEXT PRIMARY KEY,
                    paper_account_id TEXT,
                    paper_run_id TEXT,
                    record_type TEXT NOT NULL,
                    effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_paper_records_account
                    ON paper_records(paper_account_id, record_type, effective_at, record_id);

                CREATE INDEX IF NOT EXISTS idx_paper_records_run
                    ON paper_records(paper_run_id, record_type, effective_at, record_id);
                """
            )
            connection.execute(
                """
                INSERT INTO paper_store_metadata(key, value)
                VALUES ('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(_SCHEMA_VERSION),),
            )

    def save_paper_account(self, account: PaperAccount) -> None:
        self._save_record(
            record_id=account.paper_account_id,
            paper_account_id=account.paper_account_id,
            paper_run_id=None,
            record_type="paper_account",
            effective_at=account.created_at.isoformat(),
            payload_json=account.model_dump_json(),
        )

    def list_paper_accounts(self) -> tuple[PaperAccount, ...]:
        return tuple(
            PaperAccount.model_validate_json(payload)
            for payload in self._list_payloads_by_type("paper_account")
        )

    def save_approved_candidate(self, candidate: ApprovedPaperCandidate) -> None:
        self._save_record(
            record_id=candidate.approved_candidate_id,
            paper_account_id=None,
            paper_run_id=None,
            record_type="approved_candidate",
            effective_at=candidate.approved_at.isoformat(),
            payload_json=candidate.model_dump_json(),
        )

    def list_approved_candidates(self) -> tuple[ApprovedPaperCandidate, ...]:
        return tuple(
            ApprovedPaperCandidate.model_validate_json(payload)
            for payload in self._list_payloads_by_type("approved_candidate")
        )

    def save_evaluation_request(self, request: PaperEvaluationRequest) -> None:
        self._save_record(
            record_id=request.paper_run_id,
            paper_account_id=request.paper_account_id,
            paper_run_id=request.paper_run_id,
            record_type="evaluation_request",
            effective_at=request.requested_at.isoformat(),
            payload_json=request.model_dump_json(),
        )

    def list_evaluation_requests(self, paper_account_id: UUID) -> tuple[PaperEvaluationRequest, ...]:
        return tuple(
            PaperEvaluationRequest.model_validate_json(payload)
            for payload in self._list_payloads_by_account(paper_account_id, "evaluation_request")
        )

    def save_health_gate(self, gate: PaperHealthGateDecision) -> None:
        self._save_record(
            record_id=gate.health_gate_id,
            paper_account_id=None,
            paper_run_id=gate.paper_run_id,
            record_type="health_gate",
            effective_at=gate.checked_at.isoformat(),
            payload_json=gate.model_dump_json(),
        )

    def list_health_gates(self, paper_run_id: UUID) -> tuple[PaperHealthGateDecision, ...]:
        return tuple(
            PaperHealthGateDecision.model_validate_json(payload)
            for payload in self._list_payloads_by_run(paper_run_id, "health_gate")
        )

    def save_control_decision(self, decision: PaperControlDecision) -> None:
        self._save_record(
            record_id=decision.control_decision_id,
            paper_account_id=decision.paper_account_id,
            paper_run_id=None,
            record_type="control_decision",
            effective_at=decision.effective_at.isoformat(),
            payload_json=decision.model_dump_json(),
        )

    def list_control_decisions(self, paper_account_id: UUID) -> tuple[PaperControlDecision, ...]:
        return tuple(
            PaperControlDecision.model_validate_json(payload)
            for payload in self._list_payloads_by_account(paper_account_id, "control_decision")
        )

    def save_schedule(self, schedule: PaperSchedule) -> None:
        self._save_record(
            record_id=schedule.schedule_id,
            paper_account_id=schedule.paper_account_id,
            paper_run_id=schedule.paper_run_id,
            record_type="schedule",
            effective_at=schedule.starts_at.isoformat(),
            payload_json=schedule.model_dump_json(),
        )

    def list_schedules(self, paper_run_id: UUID) -> tuple[PaperSchedule, ...]:
        return tuple(
            PaperSchedule.model_validate_json(payload)
            for payload in self._list_payloads_by_run(paper_run_id, "schedule")
        )

    def save_checkpoint(self, checkpoint: PaperRunCheckpoint) -> None:
        self._save_record(
            record_id=checkpoint.checkpoint_id,
            paper_account_id=None,
            paper_run_id=checkpoint.paper_run_id,
            record_type="checkpoint",
            effective_at=checkpoint.created_at.isoformat(),
            payload_json=checkpoint.model_dump_json(),
        )

    def list_checkpoints(self, paper_run_id: UUID) -> tuple[PaperRunCheckpoint, ...]:
        return tuple(
            PaperRunCheckpoint.model_validate_json(payload)
            for payload in self._list_payloads_by_run(paper_run_id, "checkpoint")
        )

    def save_recovery_decision(self, decision: PaperRecoveryDecision) -> None:
        self._save_record(
            record_id=decision.recovery_decision_id,
            paper_account_id=None,
            paper_run_id=decision.paper_run_id,
            record_type="recovery_decision",
            effective_at=decision.decided_at.isoformat(),
            payload_json=decision.model_dump_json(),
        )

    def list_recovery_decisions(self, paper_run_id: UUID) -> tuple[PaperRecoveryDecision, ...]:
        return tuple(
            PaperRecoveryDecision.model_validate_json(payload)
            for payload in self._list_payloads_by_run(paper_run_id, "recovery_decision")
        )

    def save_forward_comparison(self, comparison: ForwardComparisonRecord) -> None:
        self._save_record(
            record_id=comparison.comparison_id,
            paper_account_id=None,
            paper_run_id=comparison.paper_run_id,
            record_type="forward_comparison",
            effective_at=comparison.compared_at.isoformat(),
            payload_json=comparison.model_dump_json(),
        )

    def list_forward_comparisons(self, paper_run_id: UUID) -> tuple[ForwardComparisonRecord, ...]:
        return tuple(
            ForwardComparisonRecord.model_validate_json(payload)
            for payload in self._list_payloads_by_run(paper_run_id, "forward_comparison")
        )

    def _save_record(
        self,
        *,
        record_id: UUID,
        paper_account_id: UUID | None,
        paper_run_id: UUID | None,
        record_type: str,
        effective_at: str,
        payload_json: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO paper_records(
                    record_id,
                    paper_account_id,
                    paper_run_id,
                    record_type,
                    effective_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET
                    paper_account_id = excluded.paper_account_id,
                    paper_run_id = excluded.paper_run_id,
                    record_type = excluded.record_type,
                    effective_at = excluded.effective_at,
                    payload_json = excluded.payload_json
                """,
                (
                    str(record_id),
                    str(paper_account_id) if paper_account_id is not None else None,
                    str(paper_run_id) if paper_run_id is not None else None,
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
                FROM paper_records
                WHERE record_type = ?
                ORDER BY effective_at, record_id
                """,
                (record_type,),
            ).fetchall()
        return tuple(cast(str, row["payload_json"]) for row in rows)

    def _list_payloads_by_account(self, paper_account_id: UUID, record_type: str) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM paper_records
                WHERE paper_account_id = ? AND record_type = ?
                ORDER BY effective_at, record_id
                """,
                (str(paper_account_id), record_type),
            ).fetchall()
        return tuple(cast(str, row["payload_json"]) for row in rows)

    def _list_payloads_by_run(self, paper_run_id: UUID, record_type: str) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM paper_records
                WHERE paper_run_id = ? AND record_type = ?
                ORDER BY effective_at, record_id
                """,
                (str(paper_run_id), record_type),
            ).fetchall()
        return tuple(cast(str, row["payload_json"]) for row in rows)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection
