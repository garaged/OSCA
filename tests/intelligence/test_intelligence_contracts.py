from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.intelligence import (
    AnalysisPackFamily,
    AnalysisPackManifest,
    AnalyticalResultBundle,
    EvidenceKind,
    EvidenceReference,
    MethodComparisonOutcome,
    MethodologyDisclosure,
    PackDataRequirement,
    PortfolioScenarioReport,
    VisualizationPackSpec,
    calibrate_outcome,
    compare_methods,
    synthesize_cross_family_evidence,
    validate_analysis_pack,
)


def build_manifest() -> AnalysisPackManifest:
    return AnalysisPackManifest(
        pack_id="fundamental-core",
        pack_version="1.0.0",
        pack_family=AnalysisPackFamily.FUNDAMENTAL_VALUATION,
        supported_asset_classes=("equity",),
        output_kinds=(EvidenceKind.FINDING,),
        data_requirements=(
            PackDataRequirement(
                capability="financial-statements",
                interval="quarterly",
                quality_policy_id="strict",
            ),
        ),
        methodology=MethodologyDisclosure(
            methodology_id="dcf-screen",
            methodology_version="1.0.0",
            assumptions=("discount-rate-declared",),
            limitations=("not-investment-advice",),
            documentation_uri="docs/intelligence/dcf-screen.md",
        ),
    )


def build_result(project_id: object, pack_id: str = "fundamental-core") -> AnalyticalResultBundle:
    evidence = EvidenceReference(
        evidence_id=uuid4(),
        evidence_kind=EvidenceKind.OBSERVATION,
        source_pack_id=pack_id,
        dataset_revision_ids=(uuid4(),),
        methodology_id="dcf-screen",
        confidence=0.8,
    )
    return AnalyticalResultBundle(
        project_id=project_id,
        pack_id=pack_id,
        pack_version="1.0.0",
        result_kind=EvidenceKind.FINDING,
        evidence=(evidence,),
    )


def test_analysis_pack_validation_approves_documented_manifest() -> None:
    decision = validate_analysis_pack(build_manifest())

    assert decision.approved is True
    assert decision.findings == ()


def test_analysis_pack_validation_fails_closed_without_docs() -> None:
    manifest = build_manifest().model_copy(
        update={
            "methodology": MethodologyDisclosure(
                methodology_id="dcf-screen",
                methodology_version="1.0.0",
                assumptions=("discount-rate-declared",),
                limitations=("not-investment-advice",),
                documentation_uri="missing-reference",
            )
        }
    )

    decision = validate_analysis_pack(manifest)

    assert decision.approved is False
    assert decision.findings[0].code == "missing_methodology_docs"


def test_provisional_data_is_rejected_by_default() -> None:
    with pytest.raises(ValidationError, match="provisional data"):
        PackDataRequirement(
            capability="news",
            interval="realtime",
            quality_policy_id="strict",
            allow_provisional_data=True,
        )


def test_method_comparison_requires_preferred_result_to_be_compared() -> None:
    project_id = uuid4()
    first = build_result(project_id)
    second = build_result(project_id, pack_id="macro-core")

    report = compare_methods(
        project_id=project_id,
        result_bundles=(first, second),
        preferred_result_id=uuid4(),
        rationale="candidate was not part of this review",
    )

    assert report.outcome is MethodComparisonOutcome.BLOCKED
    assert report.preferred_result_id is None
    assert report.findings[0].code == "preferred_result_not_compared"


def test_outcome_calibration_degrades_when_threshold_is_exceeded() -> None:
    project_id = uuid4()
    source_result_id = uuid4()

    report = calibrate_outcome(
        project_id=project_id,
        source_result_id=source_result_id,
        expected_outcome="upside-5pct",
        realized_outcome="flat",
        error_metric=0.4,
        warning_threshold=0.2,
    )

    assert report.calibration_status.value == "degraded"
    assert report.findings[0].code == "outcome_calibration_degraded"


def test_cross_family_synthesis_preserves_supporting_and_contradicting_evidence() -> None:
    project_id = uuid4()
    first = build_result(project_id)
    second = build_result(project_id, pack_id="macro-core")
    supporting = first.evidence
    contradicting = second.evidence

    report = synthesize_cross_family_evidence(
        project_id=project_id,
        result_bundles=(first, second),
        supporting_evidence=supporting,
        contradicting_evidence=contradicting,
        conclusion="mixed evidence requires follow-up",
    )

    assert report.included_result_ids == (first.result_bundle_id, second.result_bundle_id)
    assert report.contradicting_evidence == contradicting


def test_visualization_specs_require_accessible_summary_and_export_metadata() -> None:
    with pytest.raises(ValidationError, match="accessible summaries"):
        VisualizationPackSpec(
            pack_id="chart-pack",
            supported_result_kinds=(EvidenceKind.FINDING,),
            accessible_summary_required=False,
        )


def test_portfolio_scenario_requires_unique_exposure_metrics() -> None:
    with pytest.raises(ValidationError, match="exposure metrics"):
        PortfolioScenarioReport(
            paper_account_id=uuid4(),
            scenario_id="stress",
            base_currency="USD",
            exposure_metric_ids=("gross-exposure", "gross-exposure"),
            stress_assumption_ids=("rates-up",),
        )
