from osca.ml.contracts import (
    DatasetSplit,
    MLEvaluationReport,
    MLFinding,
    MLFindingSeverity,
    MLMetric,
    MLModelArtifact,
    MLPromotionDecision,
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
