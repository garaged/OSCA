from datetime import UTC, datetime
from uuid import uuid4

import pytest

from osca.research.api import (
    AdHocWorkspace,
    AnalysisGraph,
    AnalysisNode,
    AnalysisOutput,
    AnalysisOutputType,
    TimelineEvent,
    TimelineEventType,
    VisualizationSpec,
    VisualizationType,
)
from osca.research.application import (
    assemble_evidence_report,
    plan_analysis_graph,
    project_timeline,
    promote_ad_hoc_workspace,
)


def test_promote_ad_hoc_workspace_creates_project_promotion_and_event() -> None:
    dependency_id = uuid4()
    workspace = AdHocWorkspace(
        objective="Explore mean reversion in liquid ETFs",
        horizon="20d",
        captured_context=("Notebook scan identified a candidate universe",),
        selected_dependency_ids=(dependency_id,),
    )

    project, promotion, event = promote_ad_hoc_workspace(
        workspace,
        rationale="Promote ETF exploration into a governed project",
    )

    assert project.objective == workspace.objective
    assert project.dataset_revision_ids == (dependency_id,)
    assert promotion.project_id == project.project_id
    assert event.event_type is TimelineEventType.PROMOTION
    assert event.related_ids == (workspace.workspace_id, promotion.promotion_id)


def test_project_timeline_orders_events_deterministically() -> None:
    project_id = uuid4()
    later = TimelineEvent(
        project_id=project_id,
        event_type=TimelineEventType.DECISION,
        summary="later",
        occurred_at=datetime(2024, 1, 2, 12, tzinfo=UTC),
    )
    earlier = TimelineEvent(
        project_id=project_id,
        event_type=TimelineEventType.HYPOTHESIS,
        summary="earlier",
        occurred_at=datetime(2024, 1, 2, 11, tzinfo=UTC),
    )

    assert project_timeline((later, earlier)) == (earlier, later)


def test_plan_analysis_graph_returns_topological_order_and_rejects_invalid() -> None:
    project_id = uuid4()
    graph = AnalysisGraph(
        project_id=project_id,
        quality_policy="strict-complete-v1",
        nodes=(
            AnalysisNode(node_id="returns", node_kind="metric", output_refs=("r",)),
            AnalysisNode(
                node_id="signal",
                node_kind="signal",
                input_refs=("r",),
                output_refs=("s",),
                depends_on=("returns",),
            ),
        ),
    )

    assert plan_analysis_graph(graph).node_order == ("returns", "signal")

    invalid = AnalysisGraph(
        project_id=project_id,
        quality_policy="strict-complete-v1",
        nodes=(
            AnalysisNode(
                node_id="signal",
                node_kind="signal",
                output_refs=("s",),
                depends_on=("missing",),
            ),
        ),
    )
    with pytest.raises(ValueError, match="missing_dependency"):
        plan_analysis_graph(invalid)


def test_assemble_evidence_report_requires_project_scoped_outputs() -> None:
    project_id = uuid4()
    graph_id = uuid4()
    project = AdHocWorkspace(
        objective="Explore breakout behavior",
        horizon="10d",
        captured_context=("manual chart review",),
        selected_dependency_ids=(uuid4(),),
    )
    research_project, _, _ = promote_ad_hoc_workspace(
        project,
        rationale="Promote breakout exploration",
    )
    output = AnalysisOutput(
        output_type=AnalysisOutputType.FINDING,
        project_id=research_project.project_id,
        graph_id=graph_id,
        producer="builtin.analysis.core-v1",
        effective_at=datetime(2024, 1, 2, tzinfo=UTC),
        quality_state="valid",
        dataset_revision_ids=research_project.dataset_revision_ids,
        parameter_digest="sha256:abc",
    )
    visualization = VisualizationSpec(
        project_id=research_project.project_id,
        visualization_type=VisualizationType.TABLE,
        title="Breakout findings",
        source_output_ids=(output.output_id,),
    )

    report = assemble_evidence_report(
        project=research_project,
        title="Breakout evidence",
        outputs=(output,),
        visualizations=(visualization,),
        assumptions=("completed bars only",),
        reproduction_refs=("graph:breakout-v1",),
    )

    assert report.output_ids == (output.output_id,)
    assert report.visualization_ids == (visualization.visualization_id,)
