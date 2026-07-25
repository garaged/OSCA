from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Any, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=1024)]


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    BRANCHED = "branched"


class HypothesisState(StrEnum):
    ACTIVE = "active"
    WEAKENED = "weakened"
    INVALIDATED = "invalidated"
    EXPIRED = "expired"
    CONFIRMED = "confirmed"


class TimelineEventType(StrEnum):
    DECISION = "decision"
    HYPOTHESIS = "hypothesis"
    DATASET_REVISION = "dataset_revision"
    ANALYSIS_GRAPH = "analysis_graph"
    ANALYTICAL_OUTPUT = "analytical_output"
    VISUALIZATION = "visualization"
    REPORT = "report"
    PROMOTION = "promotion"


class AnalysisOutputType(StrEnum):
    OBSERVATION = "observation"
    SIGNAL = "signal"
    FINDING = "finding"
    THESIS = "thesis"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"
    REPORT = "report"


class VisualizationType(StrEnum):
    PRICE_CHART = "price_chart"
    TABLE = "table"
    DASHBOARD = "dashboard"
    HEATMAP = "heatmap"
    DISTRIBUTION = "distribution"


class ResearchProject(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.research.project"] = "osca.research.project"
    version: Literal["1.0.0"] = "1.0.0"
    project_id: UUID = Field(default_factory=uuid4)
    objective: Description
    horizon: Identifier
    status: ProjectStatus = ProjectStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    default_interval: Identifier | None = None
    dataset_revision_ids: tuple[UUID, ...] = ()

    @model_validator(mode="after")
    def validate_created_at(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        return self


class Hypothesis(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.research.hypothesis"] = "osca.research.hypothesis"
    version: Literal["1.0.0"] = "1.0.0"
    hypothesis_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    statement: Description
    assumptions: tuple[Description, ...] = Field(min_length=1)
    expected_outcomes: tuple[Description, ...] = Field(min_length=1)
    invalidation_conditions: tuple[Description, ...] = Field(min_length=1)
    confidence: Annotated[float, Field(ge=0, le=1)]
    state: HypothesisState = HypothesisState.ACTIVE


class TimelineEvent(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.research.timeline-event"] = "osca.research.timeline-event"
    version: Literal["1.0.0"] = "1.0.0"
    event_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    event_type: TimelineEventType
    summary: Description
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    related_ids: tuple[UUID, ...] = ()

    @model_validator(mode="after")
    def validate_occurred_at(self) -> Self:
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware")
        return self


class AdHocWorkspace(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.research.ad-hoc-workspace"] = "osca.research.ad-hoc-workspace"
    version: Literal["1.0.0"] = "1.0.0"
    workspace_id: UUID = Field(default_factory=uuid4)
    objective: Description
    horizon: Identifier
    captured_context: tuple[Description, ...] = Field(min_length=1)
    selected_dependency_ids: tuple[UUID, ...] = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_created_at(self) -> Self:
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        return self


class ProjectPromotion(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.research.project-promotion"] = (
        "osca.research.project-promotion"
    )
    version: Literal["1.0.0"] = "1.0.0"
    promotion_id: UUID = Field(default_factory=uuid4)
    workspace_id: UUID
    project_id: UUID
    rationale: Description
    selected_dependency_ids: tuple[UUID, ...] = Field(min_length=1)
    promoted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_promoted_at(self) -> Self:
        if self.promoted_at.tzinfo is None:
            raise ValueError("promoted_at must be timezone-aware")
        return self


class AnalysisNode(BaseModel):
    model_config = ConfigDict(frozen=True)
    node_id: Identifier
    node_kind: Identifier
    input_refs: tuple[Identifier, ...] = ()
    output_refs: tuple[Identifier, ...] = Field(min_length=1)
    depends_on: tuple[Identifier, ...] = ()
    parameters: dict[str, Any] = Field(default_factory=dict)
    required_intervals: tuple[Identifier, ...] = ()
    allow_provisional_data: bool = False


class GraphValidationFinding(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: Identifier
    message: Description
    node_id: Identifier | None = None


class AnalysisGraph(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.analysis.graph"] = "osca.analysis.graph"
    version: Literal["1.0.0"] = "1.0.0"
    graph_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    nodes: tuple[AnalysisNode, ...] = Field(min_length=1)
    quality_policy: Identifier
    require_complete_data: bool = True

    def validate_graph(self) -> tuple[GraphValidationFinding, ...]:
        findings: list[GraphValidationFinding] = []
        node_ids = [node.node_id for node in self.nodes]
        duplicates = {node_id for node_id in node_ids if node_ids.count(node_id) > 1}
        findings.extend(
            GraphValidationFinding(
                code="duplicate_node",
                message=f"duplicate analysis node: {node_id}",
                node_id=node_id,
            )
            for node_id in sorted(duplicates)
        )
        known = set(node_ids)
        output_refs = {ref for node in self.nodes for ref in node.output_refs}
        for node in self.nodes:
            for dependency in node.depends_on:
                if dependency not in known:
                    findings.append(
                        GraphValidationFinding(
                            code="missing_dependency",
                            message=f"missing dependency: {dependency}",
                            node_id=node.node_id,
                        )
                    )
            for input_ref in node.input_refs:
                if input_ref not in output_refs:
                    findings.append(
                        GraphValidationFinding(
                            code="missing_input",
                            message=f"missing input reference: {input_ref}",
                            node_id=node.node_id,
                        )
                    )
            if self.require_complete_data and node.allow_provisional_data:
                findings.append(
                    GraphValidationFinding(
                        code="provisional_data_not_allowed",
                        message="node allows provisional data under complete-data policy",
                        node_id=node.node_id,
                    )
                )
        findings.extend(_cycle_findings(self.nodes))
        return tuple(findings)


class AnalysisOutput(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.analysis.output"] = "osca.analysis.output"
    version: Literal["1.0.0"] = "1.0.0"
    output_id: UUID = Field(default_factory=uuid4)
    output_type: AnalysisOutputType
    project_id: UUID
    graph_id: UUID
    producer: Identifier
    effective_at: datetime
    quality_state: Identifier
    dataset_revision_ids: tuple[UUID, ...] = Field(min_length=1)
    parameter_digest: Identifier
    evidence_refs: tuple[Identifier, ...] = ()

    @model_validator(mode="after")
    def validate_effective_at(self) -> Self:
        if self.effective_at.tzinfo is None:
            raise ValueError("effective_at must be timezone-aware")
        return self


class EvidenceReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.research.evidence-report"] = "osca.research.evidence-report"
    version: Literal["1.0.0"] = "1.0.0"
    report_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    title: Identifier
    output_ids: tuple[UUID, ...] = Field(min_length=1)
    visualization_ids: tuple[UUID, ...] = ()
    assumptions: tuple[Description, ...] = Field(min_length=1)
    contradictions: tuple[Description, ...] = ()
    reproduction_refs: tuple[Identifier, ...] = Field(min_length=1)


class VisualizationSpec(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.visualization.specification"] = (
        "osca.visualization.specification"
    )
    version: Literal["1.0.0"] = "1.0.0"
    visualization_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    visualization_type: VisualizationType
    title: Identifier
    source_output_ids: tuple[UUID, ...] = Field(min_length=1)
    encoding: dict[str, Any] = Field(default_factory=dict)
    downsampling_disclosure: Description | None = None


class DashboardPanel(BaseModel):
    model_config = ConfigDict(frozen=True)
    panel_id: Identifier
    visualization_id: UUID
    title: Identifier
    position: Annotated[int, Field(ge=0)]
    layout: dict[str, Any] = Field(default_factory=dict)


class DashboardSpec(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.visualization.dashboard"] = "osca.visualization.dashboard"
    version: Literal["1.0.0"] = "1.0.0"
    dashboard_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    title: Identifier
    panels: tuple[DashboardPanel, ...] = Field(min_length=1)
    source_visualization_ids: tuple[UUID, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_panels(self) -> Self:
        panel_ids = [panel.panel_id for panel in self.panels]
        if len(set(panel_ids)) != len(panel_ids):
            raise ValueError("dashboard panel identifiers must be unique")
        positions = [panel.position for panel in self.panels]
        if len(set(positions)) != len(positions):
            raise ValueError("dashboard panel positions must be unique")
        panel_visualization_ids = {panel.visualization_id for panel in self.panels}
        source_ids = set(self.source_visualization_ids)
        if panel_visualization_ids != source_ids:
            raise ValueError("dashboard panels must match source visualizations")
        return self


class VisualizationExport(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.visualization.export"] = "osca.visualization.export"
    version: Literal["1.0.0"] = "1.0.0"
    export_id: UUID = Field(default_factory=uuid4)
    visualization_id: UUID
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    format: Identifier
    producer: Identifier
    source_output_ids: tuple[UUID, ...] = Field(min_length=1)
    reproduction_parameters: dict[str, Any] = Field(default_factory=dict)
    aggregation_disclosure: Description

    @model_validator(mode="after")
    def validate_generated_at(self) -> Self:
        if self.generated_at.tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")
        return self


def _cycle_findings(nodes: tuple[AnalysisNode, ...]) -> tuple[GraphValidationFinding, ...]:
    by_id = {node.node_id: node for node in nodes}
    visiting: set[str] = set()
    visited: set[str] = set()
    findings: list[GraphValidationFinding] = []

    def visit(node_id: str) -> None:
        if node_id in visited or node_id not in by_id:
            return
        if node_id in visiting:
            findings.append(
                GraphValidationFinding(
                    code="dependency_cycle",
                    message=f"dependency cycle includes: {node_id}",
                    node_id=node_id,
                )
            )
            return
        visiting.add(node_id)
        for dependency in by_id[node_id].depends_on:
            visit(dependency)
        visiting.remove(node_id)
        visited.add(node_id)

    for node in nodes:
        visit(node.node_id)
    return tuple(findings)
