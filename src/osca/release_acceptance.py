from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AcceptanceStatus = Literal["pass", "fail", "blocked"]
DefectSeverity = Literal["critical", "high", "medium", "low"]

ACCEPTANCE_AREAS: tuple[str, ...] = (
    "installation-initialization",
    "no-cost-historical-acquisition",
    "local-csv-fallback",
    "dataset-quality-revision-lineage",
    "deterministic-analysis",
    "backtesting-paper-evidence",
    "ml-experiment-diagnostics",
    "human-gated-validation",
    "workspace-browsing-export",
    "backup-restore",
    "extension-boundaries",
    "offline-operation",
    "provider-outage-quota-policy",
    "corrupt-incomplete-artifacts",
    "upgrade-rollback",
    "documentation-cli-agreement",
)


class AcceptanceArea(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    area_id: str
    status: AcceptanceStatus
    summary: str
    evidence: list[str] = Field(min_length=1)
    remediation: str | None = None

    @model_validator(mode="after")
    def validate_failure_remediation(self) -> AcceptanceArea:
        if self.status != "pass" and not self.remediation:
            raise ValueError("failed or blocked acceptance areas require remediation")
        return self


class DefectDisposition(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    defect_id: str
    severity: DefectSeverity
    status: Literal["open", "closed"]
    summary: str
    workaround: str | None = None
    owner: str | None = None
    target_milestone: str | None = None

    @model_validator(mode="after")
    def validate_open_medium(self) -> DefectDisposition:
        if (
            self.status == "open"
            and self.severity == "medium"
            and not all((self.workaround, self.owner, self.target_milestone))
        ):
            raise ValueError(
                "open medium defects require workaround, owner, and target milestone"
            )
        return self


class AcceptanceInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    version: Literal["1.0.0"]
    candidate_version: str
    source_commit: str
    artifacts: list[str] = Field(min_length=1)
    areas: list[AcceptanceArea]
    defects: list[DefectDisposition] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_matrix(self) -> AcceptanceInput:
        identifiers = [area.area_id for area in self.areas]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("acceptance area identifiers must be unique")
        missing = sorted(set(ACCEPTANCE_AREAS) - set(identifiers))
        unexpected = sorted(set(identifiers) - set(ACCEPTANCE_AREAS))
        if missing or unexpected:
            raise ValueError(
                f"acceptance matrix mismatch; missing={missing}, unexpected={unexpected}"
            )
        return self


def evaluate_release_candidate(document: AcceptanceInput) -> dict[str, object]:
    failed_areas = [area.area_id for area in document.areas if area.status == "fail"]
    blocked_areas = [area.area_id for area in document.areas if area.status == "blocked"]
    blocking_defects = [
        defect.defect_id
        for defect in document.defects
        if defect.status == "open" and defect.severity in {"critical", "high"}
    ]
    undisposed_medium = [
        defect.defect_id
        for defect in document.defects
        if defect.status == "open"
        and defect.severity == "medium"
        and not all((defect.workaround, defect.owner, defect.target_milestone))
    ]
    eligible = all(
        (
            not failed_areas,
            not blocked_areas,
            not blocking_defects,
            not undisposed_medium,
        )
    )
    payload = {
        "family": "osca.release-candidate-acceptance",
        "version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "candidate_version": document.candidate_version,
        "source_commit": document.source_commit,
        "status": "eligible" if eligible else "ineligible",
        "tag_recommended": eligible,
        "recommended_tag": f"v{document.candidate_version}" if eligible else None,
        "summary": {
            "passed": sum(area.status == "pass" for area in document.areas),
            "failed": len(failed_areas),
            "blocked": len(blocked_areas),
            "open_critical_high": len(blocking_defects),
            "undisposed_medium": len(undisposed_medium),
        },
        "failed_areas": failed_areas,
        "blocked_areas": blocked_areas,
        "blocking_defects": blocking_defects,
        "undisposed_medium_defects": undisposed_medium,
        "artifacts": document.artifacts,
        "areas": [area.model_dump(mode="json") for area in document.areas],
        "defects": [defect.model_dump(mode="json") for defect in document.defects],
        "recommendations_enabled": False,
        "automatic_model_promotion_enabled": False,
        "live_model_serving_enabled": False,
        "broker_connections_enabled": False,
        "autonomous_execution_enabled": False,
        "real_capital_orders_enabled": False,
        "tag_created": False,
        "publication_performed": False,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["acceptance_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def evaluate_files(input_path: Path, output_path: Path | None = None) -> dict[str, object]:
    document = AcceptanceInput.model_validate_json(input_path.read_text(encoding="utf-8"))
    result = evaluate_release_candidate(document)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return result
