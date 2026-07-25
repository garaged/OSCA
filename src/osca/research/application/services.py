from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from osca.research.api import (
    AdHocWorkspace,
    AnalysisGraph,
    AnalysisOutput,
    DashboardPanel,
    DashboardSpec,
    EvidenceReport,
    Hypothesis,
    HypothesisState,
    ProjectPromotion,
    ResearchProject,
    TimelineEvent,
    TimelineEventType,
    VisualizationSpec,
)


class GraphExecutionPlan(BaseModel):
    model_config = ConfigDict(frozen=True)
    graph_id: UUID
    node_order: tuple[str, ...] = Field(min_length=1)


def promote_ad_hoc_workspace(
    workspace: AdHocWorkspace,
    *,
    rationale: str,
) -> tuple[ResearchProject, ProjectPromotion, TimelineEvent]:
    project = ResearchProject(
        objective=workspace.objective,
        horizon=workspace.horizon,
        dataset_revision_ids=workspace.selected_dependency_ids,
    )
    promotion = ProjectPromotion(
        workspace_id=workspace.workspace_id,
        project_id=project.project_id,
        rationale=rationale,
        selected_dependency_ids=workspace.selected_dependency_ids,
    )
    event = TimelineEvent(
        project_id=project.project_id,
        event_type=TimelineEventType.PROMOTION,
        summary=rationale,
        related_ids=(workspace.workspace_id, promotion.promotion_id),
    )
    return project, promotion, event


def transition_hypothesis(
    hypothesis: Hypothesis,
    *,
    new_state: HypothesisState,
    rationale: str,
) -> tuple[Hypothesis, TimelineEvent]:
    if hypothesis.state is new_state:
        raise ValueError("hypothesis transition requires a different state")
    updated = hypothesis.model_copy(update={"state": new_state})
    event = TimelineEvent(
        project_id=hypothesis.project_id,
        event_type=TimelineEventType.HYPOTHESIS,
        summary=rationale,
        related_ids=(hypothesis.hypothesis_id,),
    )
    return updated, event


def project_timeline(events: tuple[TimelineEvent, ...]) -> tuple[TimelineEvent, ...]:
    return tuple(sorted(events, key=lambda event: (event.occurred_at, event.event_id)))


def plan_analysis_graph(graph: AnalysisGraph) -> GraphExecutionPlan:
    findings = graph.validate_graph()
    if findings:
        codes = ", ".join(finding.code for finding in findings)
        raise ValueError(f"analysis graph is invalid: {codes}")

    by_id = {node.node_id: node for node in graph.nodes}
    planned: list[str] = []
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visited:
            return
        for dependency in by_id[node_id].depends_on:
            visit(dependency)
        visited.add(node_id)
        planned.append(node_id)

    for node in graph.nodes:
        visit(node.node_id)
    return GraphExecutionPlan(graph_id=graph.graph_id, node_order=tuple(planned))


def assemble_evidence_report(
    *,
    project: ResearchProject,
    title: str,
    outputs: tuple[AnalysisOutput, ...],
    visualizations: tuple[VisualizationSpec, ...],
    assumptions: tuple[str, ...],
    contradictions: tuple[str, ...] = (),
    reproduction_refs: tuple[str, ...],
) -> EvidenceReport:
    if not outputs:
        raise ValueError("evidence report requires at least one analytical output")
    if any(output.project_id != project.project_id for output in outputs):
        raise ValueError("all report outputs must belong to the project")
    if any(
        visualization.project_id != project.project_id for visualization in visualizations
    ):
        raise ValueError("all report visualizations must belong to the project")
    output_ids = tuple(output.output_id for output in outputs)
    for visualization in visualizations:
        unknown = set(visualization.source_output_ids).difference(output_ids)
        if unknown:
            raise ValueError("visualization references outputs outside the report")
    return EvidenceReport(
        project_id=project.project_id,
        title=title,
        output_ids=output_ids,
        visualization_ids=tuple(
            visualization.visualization_id for visualization in visualizations
        ),
        assumptions=assumptions,
        contradictions=contradictions,
        reproduction_refs=reproduction_refs,
    )


def compose_dashboard(
    *,
    project: ResearchProject,
    title: str,
    visualizations: tuple[VisualizationSpec, ...],
) -> DashboardSpec:
    if not visualizations:
        raise ValueError("dashboard requires at least one visualization")
    if any(
        visualization.project_id != project.project_id for visualization in visualizations
    ):
        raise ValueError("all dashboard visualizations must belong to the project")
    panels = tuple(
        DashboardPanel(
            panel_id=f"panel-{index + 1}",
            visualization_id=visualization.visualization_id,
            title=visualization.title,
            position=index,
        )
        for index, visualization in enumerate(visualizations)
    )
    return DashboardSpec(
        project_id=project.project_id,
        title=title,
        panels=panels,
        source_visualization_ids=tuple(
            visualization.visualization_id for visualization in visualizations
        ),
    )
