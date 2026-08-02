from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Identifier = Annotated[str, Field(min_length=1, max_length=256)]
Description = Annotated[str, Field(min_length=1, max_length=4096)]
LocalPath = Annotated[str, Field(min_length=1, max_length=4096)]


class WorkspaceSection(StrEnum):
    PROJECTS = "projects"
    WATCHLISTS = "watchlists"
    DATASETS = "datasets"
    ACQUISITIONS = "acquisitions"
    BACKTESTS = "backtests"
    EXPERIMENTS = "experiments"
    DIAGNOSTICS = "diagnostics"
    VALIDATIONS = "validations"
    PIPELINE_RUNS = "pipeline_runs"
    REPORTS = "reports"
    ENRICHMENT = "enrichment"
    ROUTING = "routing"


class WorkspaceItemStatus(StrEnum):
    AVAILABLE = "available"
    EMPTY = "empty"
    WARNING = "warning"
    REVIEW_REQUIRED = "review_required"
    NOT_ELIGIBLE = "not_eligible"
    INCOMPLETE = "incomplete"
    CORRUPT = "corrupt"
    INCOMPATIBLE = "incompatible"
    ORPHANED = "orphaned"
    POLICY_BLOCKED = "policy_blocked"
    PROVIDER_UNAVAILABLE = "provider_unavailable"


class WorkspaceItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    item_id: Identifier
    section: WorkspaceSection
    title: Identifier
    status: WorkspaceItemStatus
    summary: Description
    artifact_uri: LocalPath | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class WorkspaceSectionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    section: WorkspaceSection
    items: tuple[WorkspaceItem, ...]
    item_count: int = Field(ge=0)
    empty_message: Description


class AnalystWorkspaceSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.analyst-workspace.snapshot"] = (
        "osca.analyst-workspace.snapshot"
    )
    version: Literal["1.1.0"] = "1.1.0"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    storage_root: LocalPath
    sections: tuple[WorkspaceSectionResult, ...]
    total_items: int = Field(ge=0)
    warnings: tuple[Description, ...] = ()
    read_only: Literal[True] = True
    network_access_enabled: Literal[False] = False
    credential_materialization_enabled: Literal[False] = False
    production_ingestion_enabled: Literal[False] = False
    recommendations_enabled: Literal[False] = False
    broker_connections_enabled: Literal[False] = False
    real_capital_orders_enabled: Literal[False] = False
