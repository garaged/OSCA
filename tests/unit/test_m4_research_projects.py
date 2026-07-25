from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.research.api import (
    AnalysisGraph,
    AnalysisNode,
    AnalysisOutput,
    AnalysisOutputType,
    Hypothesis,
    HypothesisState,
    ResearchProject,
    TimelineEvent,
    TimelineEventType,
    VisualizationExport,
    VisualizationSpec,
    VisualizationType,
)


def test_project_hypothesis_and_timeline_have_governed_identity() -> None:
    project = ResearchProject(objective="Compare momentum behavior for liquid stocks", horizon="30d")
    hypothesis = Hypothesis(
        project_id=project.project_id,
        statement="Recent winners continue outperforming over the next month",
        assumptions=("liquidity remains comparable",),
        expected_outcomes=("top-decile momentum basket outperforms benchmark",),
        invalidation_conditions=("benchmark outperforms after costs",),
        confidence=0.55,
    )
    event = TimelineEvent(
        project_id=project.project_id,
        event_type=TimelineEventType.HYPOTHESIS,
        summary="Recorded initial momentum hypothesis",
        related_ids=(hypothesis.hypothesis_id,),
    )

    assert project.status == "active"
    assert hypothesis.state is HypothesisState.ACTIVE
    assert event.related_ids == (hypothesis.hypothesis_id,)


def test_analysis_graph_validation_detects_cycles_missing_dependencies_and_policy() -> None:
    graph = AnalysisGraph(
        project_id=uuid4(),
        quality_policy="strict-complete-v1",
        nodes=(
            AnalysisNode(
                node_id="returns",
                node_kind="metric",
                output_refs=("returns.output",),
                depends_on=("signal",),
            ),
            AnalysisNode(
                node_id="signal",
                node_kind="signal",
                input_refs=("returns.output",),
                output_refs=("signal.output",),
                depends_on=("returns", "missing-node"),
                allow_provisional_data=True,
            ),
        ),
    )

    codes = {finding.code for finding in graph.validate_graph()}
    assert codes == {
        "dependency_cycle",
        "missing_dependency",
        "provisional_data_not_allowed",
    }


def test_analysis_output_requires_dataset_lineage_and_utc_effective_time() -> None:
    project_id = uuid4()
    graph_id = uuid4()

    output = AnalysisOutput(
        output_type=AnalysisOutputType.FINDING,
        project_id=project_id,
        graph_id=graph_id,
        producer="builtin.analysis.core-v1",
        effective_at=datetime(2024, 1, 2, tzinfo=UTC),
        quality_state="valid",
        dataset_revision_ids=(uuid4(),),
        parameter_digest="sha256:abc",
        evidence_refs=("returns.output",),
    )

    assert output.output_type == AnalysisOutputType.FINDING
    with pytest.raises(ValidationError):
        AnalysisOutput(
            output_type=AnalysisOutputType.SIGNAL,
            project_id=project_id,
            graph_id=graph_id,
            producer="builtin.analysis.core-v1",
            effective_at=datetime(2024, 1, 2),
            quality_state="valid",
            dataset_revision_ids=(uuid4(),),
            parameter_digest="sha256:def",
        )


def test_visualization_spec_and_export_reference_outputs() -> None:
    output_id = uuid4()
    visualization = VisualizationSpec(
        project_id=uuid4(),
        visualization_type=VisualizationType.PRICE_CHART,
        title="Momentum comparison",
        source_output_ids=(output_id,),
        encoding={"x": "effective_at", "y": "signal_strength"},
        downsampling_disclosure="No downsampling applied",
    )
    export = VisualizationExport(
        visualization_id=visualization.visualization_id,
        format="png",
        producer="builtin.visualization.core-v1",
        source_output_ids=visualization.source_output_ids,
        reproduction_parameters={"theme": "default"},
        aggregation_disclosure="No aggregation applied",
    )

    assert export.source_output_ids == (output_id,)
    assert export.aggregation_disclosure == "No aggregation applied"
