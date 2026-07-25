from osca.intelligence.contracts import (
    AnalysisPackManifest,
    AnalyticalResultBundle,
    CalibrationStatus,
    CrossFamilySynthesisReport,
    EvidenceReference,
    IntelligenceFinding,
    IntelligenceFindingSeverity,
    IntelligenceStatus,
    MethodComparisonOutcome,
    MethodComparisonReport,
    OutcomeCalibrationReport,
    PackValidationDecision,
)


def validate_analysis_pack(manifest: AnalysisPackManifest) -> PackValidationDecision:
    findings: list[IntelligenceFinding] = []
    if not manifest.methodology.documentation_uri.startswith(("docs/", "http://", "https://")):
        findings.append(
            _error("missing_methodology_docs", "analysis pack methodology documentation is not reachable")
        )
    if manifest.pack_family.value == "cross_family_synthesis" and not manifest.supports_cross_family_synthesis:
        findings.append(
            _error("synthesis_flag_missing", "cross-family synthesis pack must declare synthesis support")
        )

    if findings:
        return PackValidationDecision(
            pack_id=manifest.pack_id,
            pack_version=manifest.pack_version,
            approved=False,
            status=IntelligenceStatus.BLOCKED,
            rationale="analysis pack validation failed closed",
            findings=tuple(findings),
        )

    return PackValidationDecision(
        pack_id=manifest.pack_id,
        pack_version=manifest.pack_version,
        approved=True,
        status=IntelligenceStatus.APPROVED,
        rationale="analysis pack manifest passed deterministic validation",
    )


def compare_methods(
    *,
    project_id: object,
    result_bundles: tuple[AnalyticalResultBundle, ...],
    preferred_result_id: object | None = None,
    rationale: str,
) -> MethodComparisonReport:
    result_ids = tuple(bundle.result_bundle_id for bundle in result_bundles)
    if preferred_result_id is None:
        outcome = MethodComparisonOutcome.COMPARABLE
    elif preferred_result_id in result_ids:
        outcome = MethodComparisonOutcome.PREFERRED
    else:
        outcome = MethodComparisonOutcome.BLOCKED

    findings = ()
    if outcome is MethodComparisonOutcome.BLOCKED:
        findings = (_error("preferred_result_not_compared", "preferred result was not compared"),)

    return MethodComparisonReport(
        project_id=project_id,
        compared_result_ids=result_ids,
        preferred_result_id=None if outcome is MethodComparisonOutcome.BLOCKED else preferred_result_id,
        outcome=outcome,
        rationale=rationale,
        findings=findings,
    )


def calibrate_outcome(
    *,
    project_id: object,
    source_result_id: object,
    expected_outcome: str,
    realized_outcome: str,
    error_metric: float,
    warning_threshold: float,
) -> OutcomeCalibrationReport:
    status = (
        CalibrationStatus.CALIBRATED
        if error_metric <= warning_threshold
        else CalibrationStatus.DEGRADED
    )
    findings = ()
    if status is CalibrationStatus.DEGRADED:
        findings = (_warning("outcome_calibration_degraded", "realized outcome exceeded threshold"),)
    return OutcomeCalibrationReport(
        project_id=project_id,
        source_result_id=source_result_id,
        expected_outcome=expected_outcome,
        realized_outcome=realized_outcome,
        calibration_status=status,
        error_metric=error_metric,
        findings=findings,
    )


def synthesize_cross_family_evidence(
    *,
    project_id: object,
    result_bundles: tuple[AnalyticalResultBundle, ...],
    supporting_evidence: tuple[EvidenceReference, ...],
    contradicting_evidence: tuple[EvidenceReference, ...] = (),
    conclusion: str,
) -> CrossFamilySynthesisReport:
    return CrossFamilySynthesisReport(
        project_id=project_id,
        included_result_ids=tuple(bundle.result_bundle_id for bundle in result_bundles),
        supporting_evidence=supporting_evidence,
        contradicting_evidence=contradicting_evidence,
        conclusion=conclusion,
    )


def _error(code: str, message: str) -> IntelligenceFinding:
    return IntelligenceFinding(
        code=code,
        severity=IntelligenceFindingSeverity.ERROR,
        message=message,
    )


def _warning(code: str, message: str) -> IntelligenceFinding:
    return IntelligenceFinding(
        code=code,
        severity=IntelligenceFindingSeverity.WARNING,
        message=message,
    )
