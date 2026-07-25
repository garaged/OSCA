from uuid import UUID

from osca.ml.contracts import (
    DatasetSplit,
    MLDeploymentRole,
    MLDriftMetric,
    MLEvaluationReport,
    MLEventValidationLink,
    MLFinding,
    MLFindingSeverity,
    MLMetric,
    MLModelArtifact,
    MLMonitoringReport,
    MLMonitoringStatus,
    MLPaperDeploymentDecision,
    MLPromotionDecision,
    MLRetrainingRecord,
    MLRetrainingTrigger,
)


def build_evaluation_report(
    *,
    artifact: MLModelArtifact,
    metrics: tuple[MLMetric, ...],
    calibration_methodology: str,
) -> MLEvaluationReport:
    return MLEvaluationReport(
        model_artifact_id=artifact.model_artifact_id,
        experiment_run_id=artifact.experiment_run_id,
        metrics=metrics,
        calibration_methodology=calibration_methodology,
    )


def evaluate_ml_promotion(
    *,
    report: MLEvaluationReport,
    artifact: MLModelArtifact,
    minimum_holdout_metric: float,
    holdout_metric_name: str,
    rationale: str = "ML promotion evaluated",
    findings: tuple[MLFinding, ...] = (),
) -> MLPromotionDecision:
    error_findings = tuple(
        finding for finding in findings if finding.severity is MLFindingSeverity.ERROR
    )
    holdout_values = tuple(
        metric.value
        for metric in report.metrics
        if metric.split is DatasetSplit.HOLDOUT and metric.name == holdout_metric_name
    )
    threshold_passed = bool(holdout_values) and max(holdout_values) >= minimum_holdout_metric
    approved = threshold_passed and not error_findings
    return MLPromotionDecision(
        model_artifact_id=artifact.model_artifact_id,
        evaluation_report_id=report.evaluation_report_id,
        approved_for_event_validation=approved,
        approved_for_paper_challenger=False,
        rationale=rationale,
        findings=findings,
    )


def link_model_to_event_validation(
    *,
    promotion: MLPromotionDecision,
    f2_request_id: UUID,
    f2_promotion_gate_id: UUID,
) -> MLEventValidationLink:
    if not promotion.approved_for_event_validation:
        raise ValueError("event validation link requires approved ML promotion")
    return MLEventValidationLink(
        model_artifact_id=promotion.model_artifact_id,
        promotion_decision_id=promotion.promotion_decision_id,
        f2_request_id=f2_request_id,
        f2_promotion_gate_id=f2_promotion_gate_id,
    )


def decide_paper_deployment(
    *,
    promotion: MLPromotionDecision,
    paper_account_id: UUID,
    paper_run_id: UUID,
    role: MLDeploymentRole,
    rationale: str = "ML paper deployment evaluated",
    findings: tuple[MLFinding, ...] = (),
) -> MLPaperDeploymentDecision:
    has_error = any(finding.severity is MLFindingSeverity.ERROR for finding in findings)
    approved = promotion.approved_for_event_validation and not has_error
    return MLPaperDeploymentDecision(
        model_artifact_id=promotion.model_artifact_id,
        paper_account_id=paper_account_id,
        paper_run_id=paper_run_id,
        role=role,
        approved_for_paper=approved,
        promotion_decision_id=promotion.promotion_decision_id,
        rationale=rationale,
        findings=findings,
    )


def build_monitoring_report(
    *,
    model_artifact_id: UUID,
    paper_run_id: UUID,
    drift_metrics: tuple[MLDriftMetric, ...] = (),
    outcome_metrics: tuple[MLMetric, ...] = (),
    findings: tuple[MLFinding, ...] = (),
) -> MLMonitoringReport:
    has_error = any(finding.severity is MLFindingSeverity.ERROR for finding in findings)
    threshold_breached = any(metric.value > metric.threshold for metric in drift_metrics)
    status = (
        MLMonitoringStatus.BLOCKED
        if has_error
        else MLMonitoringStatus.DEGRADED
        if threshold_breached
        else MLMonitoringStatus.HEALTHY
    )
    return MLMonitoringReport(
        model_artifact_id=model_artifact_id,
        paper_run_id=paper_run_id,
        status=status,
        drift_metrics=drift_metrics,
        outcome_metrics=outcome_metrics,
        findings=findings,
    )


def request_retraining(
    *,
    source_model_artifact_id: UUID,
    trigger: MLRetrainingTrigger,
    workflow_id: str,
    rationale: str,
) -> MLRetrainingRecord:
    return MLRetrainingRecord(
        source_model_artifact_id=source_model_artifact_id,
        trigger=trigger,
        workflow_id=workflow_id,
        automatic_promotion_requested=False,
        rationale=rationale,
    )
