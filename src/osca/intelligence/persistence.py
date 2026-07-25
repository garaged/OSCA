import sqlite3
from pathlib import Path

from osca.intelligence.contracts import (
    AnalysisPackManifest,
    AnalyticalResultBundle,
    CrossFamilySynthesisReport,
    MethodComparisonReport,
    OutcomeCalibrationReport,
    PackValidationDecision,
    PortfolioScenarioReport,
    VisualizationPackSpec,
)

_SCHEMA_VERSION = 1


class SQLiteIntelligenceStore:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS intelligence_store_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS intelligence_records (
                    record_id TEXT PRIMARY KEY,
                    project_id TEXT,
                    pack_id TEXT,
                    paper_account_id TEXT,
                    record_type TEXT NOT NULL,
                    effective_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_intelligence_records_project
                    ON intelligence_records(project_id, record_type, effective_at, record_id);

                CREATE INDEX IF NOT EXISTS idx_intelligence_records_pack
                    ON intelligence_records(pack_id, record_type, effective_at, record_id);

                CREATE INDEX IF NOT EXISTS idx_intelligence_records_paper
                    ON intelligence_records(paper_account_id, record_type, effective_at, record_id);
                """
            )
            connection.execute(
                """
                INSERT INTO intelligence_store_metadata(key, value)
                VALUES ('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(_SCHEMA_VERSION),),
            )

    def save_pack_manifest(self, manifest: AnalysisPackManifest) -> None:
        self._save_record(
            record_id=f"{manifest.pack_id}:{manifest.pack_version}",
            project_id=None,
            pack_id=manifest.pack_id,
            paper_account_id=None,
            record_type="pack_manifest",
            effective_at=manifest.created_at.isoformat(),
            payload_json=manifest.model_dump_json(),
        )

    def list_pack_manifests(self) -> tuple[AnalysisPackManifest, ...]:
        return tuple(
            AnalysisPackManifest.model_validate_json(payload)
            for payload in self._list_payloads_by_type("pack_manifest")
        )

    def save_pack_validation(self, decision: PackValidationDecision) -> None:
        self._save_record(
            record_id=decision.validation_decision_id,
            project_id=None,
            pack_id=decision.pack_id,
            paper_account_id=None,
            record_type="pack_validation",
            effective_at=decision.decided_at.isoformat(),
            payload_json=decision.model_dump_json(),
        )

    def save_result_bundle(self, bundle: AnalyticalResultBundle) -> None:
        self._save_record(
            record_id=bundle.result_bundle_id,
            project_id=bundle.project_id,
            pack_id=bundle.pack_id,
            paper_account_id=None,
            record_type="result_bundle",
            effective_at=bundle.generated_at.isoformat(),
            payload_json=bundle.model_dump_json(),
        )

    def list_result_bundles(self, project_id: str) -> tuple[AnalyticalResultBundle, ...]:
        return tuple(
            AnalyticalResultBundle.model_validate_json(payload)
            for payload in self._list_payloads_by_project(project_id, "result_bundle")
        )

    def save_method_comparison(self, report: MethodComparisonReport) -> None:
        self._save_record(
            record_id=report.comparison_report_id,
            project_id=report.project_id,
            pack_id=None,
            paper_account_id=None,
            record_type="method_comparison",
            effective_at=report.compared_at.isoformat(),
            payload_json=report.model_dump_json(),
        )

    def list_method_comparisons(self, project_id: str) -> tuple[MethodComparisonReport, ...]:
        return tuple(
            MethodComparisonReport.model_validate_json(payload)
            for payload in self._list_payloads_by_project(project_id, "method_comparison")
        )

    def save_outcome_calibration(self, report: OutcomeCalibrationReport) -> None:
        self._save_record(
            record_id=report.calibration_report_id,
            project_id=report.project_id,
            pack_id=None,
            paper_account_id=None,
            record_type="outcome_calibration",
            effective_at=report.calibrated_at.isoformat(),
            payload_json=report.model_dump_json(),
        )

    def save_portfolio_scenario(self, report: PortfolioScenarioReport) -> None:
        self._save_record(
            record_id=report.scenario_report_id,
            project_id=None,
            pack_id=None,
            paper_account_id=report.paper_account_id,
            record_type="portfolio_scenario",
            effective_at=report.evaluated_at.isoformat(),
            payload_json=report.model_dump_json(),
        )

    def list_portfolio_scenarios(self, paper_account_id: str) -> tuple[PortfolioScenarioReport, ...]:
        return tuple(
            PortfolioScenarioReport.model_validate_json(payload)
            for payload in self._list_payloads_by_paper(paper_account_id, "portfolio_scenario")
        )

    def save_cross_family_synthesis(self, report: CrossFamilySynthesisReport) -> None:
        self._save_record(
            record_id=report.synthesis_report_id,
            project_id=report.project_id,
            pack_id=None,
            paper_account_id=None,
            record_type="cross_family_synthesis",
            effective_at=report.synthesized_at.isoformat(),
            payload_json=report.model_dump_json(),
        )

    def save_visualization_pack_spec(self, spec: VisualizationPackSpec) -> None:
        self._save_record(
            record_id=spec.visualization_spec_id,
            project_id=None,
            pack_id=spec.pack_id,
            paper_account_id=None,
            record_type="visualization_pack_spec",
            effective_at="0001-01-01T00:00:00+00:00",
            payload_json=spec.model_dump_json(),
        )

    def _save_record(
        self,
        *,
        record_id: object,
        project_id: object | None,
        pack_id: object | None,
        paper_account_id: object | None,
        record_type: str,
        effective_at: str,
        payload_json: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO intelligence_records(
                    record_id,
                    project_id,
                    pack_id,
                    paper_account_id,
                    record_type,
                    effective_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(record_id) DO UPDATE SET
                    project_id = excluded.project_id,
                    pack_id = excluded.pack_id,
                    paper_account_id = excluded.paper_account_id,
                    record_type = excluded.record_type,
                    effective_at = excluded.effective_at,
                    payload_json = excluded.payload_json
                """,
                (
                    str(record_id),
                    None if project_id is None else str(project_id),
                    None if pack_id is None else str(pack_id),
                    None if paper_account_id is None else str(paper_account_id),
                    record_type,
                    effective_at,
                    payload_json,
                ),
            )

    def _list_payloads_by_type(self, record_type: str) -> tuple[str, ...]:
        return self._list_payloads("record_type = ?", (record_type,))

    def _list_payloads_by_project(self, project_id: str, record_type: str) -> tuple[str, ...]:
        return self._list_payloads(
            "project_id = ? AND record_type = ?",
            (project_id, record_type),
        )

    def _list_payloads_by_paper(self, paper_account_id: str, record_type: str) -> tuple[str, ...]:
        return self._list_payloads(
            "paper_account_id = ? AND record_type = ?",
            (paper_account_id, record_type),
        )

    def _list_payloads(self, where_clause: str, parameters: tuple[str, ...]) -> tuple[str, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT payload_json
                FROM intelligence_records
                WHERE {where_clause}
                ORDER BY effective_at, record_id
                """,
                parameters,
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)
