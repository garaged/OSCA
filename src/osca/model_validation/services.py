from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable

from osca.analytical_data import ChartSeriesRequest, build_chart_series
from osca.ml_experiments import ExperimentTask, PredictionRecord
from osca.prediction_lab import DiagnosticStatus
from osca.model_validation.contracts import (
    ModelValidationRequest,
    ModelValidationResult,
    PaperChallengerEvidence,
    ResearchSignalEvent,
    ValidationStatus,
    ValidationSummary,
)


def validate_model_research(request: ModelValidationRequest) -> ModelValidationResult:
    _validate_gate(request)
    series = build_chart_series(
        ChartSeriesRequest(
            dataset_revision_id=request.experiment.dataset_revision_id,
            payload_path=request.payload_path,
            symbol=request.experiment.symbol,
            timeframe=request.experiment.timeframe,
            max_rows=50_000,
        )
    )
    rows_by_timestamp = {row.timestamp: index for index, row in enumerate(series.rows)}
    test_predictions = tuple(
        item for item in request.experiment.predictions if item.split == "test"
    )
    events: list[ResearchSignalEvent] = []
    skipped = 0
    previous_position = 0
    position_changes = 0
    equity = request.initial_cash
    peak = equity
    maximum_drawdown = 0.0
    total_cost_return = 0.0

    for prediction in test_predictions:
        source_index = rows_by_timestamp.get(prediction.timestamp)
        execution_index = (
            None
            if source_index is None
            else source_index + request.signal_rule.latency_bars
        )
        if execution_index is None or execution_index >= len(series.rows):
            skipped += 1
            continue
        execution_row = series.rows[execution_index]
        position = _position(prediction, request.signal_rule.threshold)
        changed = position != previous_position
        if changed:
            position_changes += 1
        cost_return = (
            (request.signal_rule.transaction_cost_bps + request.signal_rule.slippage_bps)
            / 10_000.0
            if changed
            else 0.0
        )
        gross_return = (
            execution_row.close / execution_row.open - 1.0 if position == 1 else 0.0
        )
        net_return = gross_return - cost_return
        equity *= 1.0 + net_return
        peak = max(peak, equity)
        maximum_drawdown = min(maximum_drawdown, equity / peak - 1.0)
        total_cost_return += cost_return
        events.append(
            ResearchSignalEvent(
                prediction_timestamp=prediction.timestamp,
                execution_timestamp=execution_row.timestamp,
                prediction=prediction.prediction,
                probability=prediction.probability,
                position=position,
                execution_price=execution_row.open,
                exit_price=execution_row.close,
                gross_return=gross_return,
                cost_return=cost_return,
                net_return=net_return,
            )
        )
        previous_position = position

    if not events:
        raise ValueError("no retained test predictions align to executable bars")

    first = events[0]
    last = events[-1]
    buy_and_hold_return = last.exit_price / first.execution_price - 1.0
    total_return = equity / request.initial_cash - 1.0
    findings = _findings(total_return, buy_and_hold_return, skipped, len(test_predictions))
    paper = PaperChallengerEvidence(
        requested=request.request_paper_challenger,
        approved=request.request_paper_challenger,
        reviewer=request.paper_challenger_reviewer,
        rationale=request.paper_challenger_rationale,
    )
    status = (
        ValidationStatus.PAPER_CHALLENGER_APPROVED
        if paper.approved
        else ValidationStatus.COMPLETED
    )
    assumptions = (
        "Retained test predictions are translated by the versioned signal rule.",
        "Signals are executed after the configured whole-bar latency at the next eligible open.",
        "Each invested period exits at the same bar close; missing predictions remain in cash.",
        "Transaction-cost and slippage assumptions apply on position changes.",
        "Buy-and-hold is a descriptive baseline over the aligned execution window.",
        "Paper challenger approval is human evidence only and enables no broker or order path.",
    )
    summary = ValidationSummary(
        aligned_predictions=len(events),
        skipped_predictions=skipped,
        invested_periods=sum(item.position for item in events),
        position_changes=position_changes,
        initial_cash=request.initial_cash,
        final_equity=equity,
        total_return=total_return,
        buy_and_hold_return=buy_and_hold_return,
        baseline_excess_return=total_return - buy_and_hold_return,
        maximum_drawdown=maximum_drawdown,
        total_cost_return=total_cost_return,
    )
    payload = {
        "experiment_id": str(request.experiment.experiment_id),
        "diagnostic_digest": request.diagnostic.diagnostic_digest,
        "promotion_decision_id": str(request.promotion.decision_id),
        "payload_sha256": series.payload_sha256,
        "signal_rule": request.signal_rule.model_dump(mode="json"),
        "events": [item.model_dump(mode="json") for item in events],
        "summary": summary.model_dump(mode="json"),
        "paper_challenger": paper.model_dump(mode="json"),
        "findings": findings,
        "assumptions": assumptions,
    }
    return ModelValidationResult(
        status=status,
        experiment_id=request.experiment.experiment_id,
        diagnostic_digest=request.diagnostic.diagnostic_digest,
        promotion_decision_id=request.promotion.decision_id,
        dataset_revision_id=request.experiment.dataset_revision_id,
        payload_sha256=series.payload_sha256,
        symbol=request.experiment.symbol,
        timeframe=request.experiment.timeframe,
        signal_rule=request.signal_rule,
        events=tuple(events),
        summary=summary,
        paper_challenger=paper,
        findings=findings,
        assumptions=assumptions,
        evidence_digest=_digest(payload),
    )


def _validate_gate(request: ModelValidationRequest) -> None:
    if request.experiment.experiment_id != request.diagnostic.experiment_id:
        raise ValueError("diagnostic does not belong to the supplied experiment")
    if request.experiment.task is not ExperimentTask.CLASSIFICATION:
        raise ValueError("U7 initial signal translation requires a classification experiment")
    if request.diagnostic.status is not DiagnosticStatus.ELIGIBLE_FOR_F2_VALIDATION:
        raise ValueError("diagnostic is not eligible for F2 validation")
    if not request.promotion.approved:
        raise ValueError("an approved human promotion decision is required")


def _position(prediction: PredictionRecord, threshold: float) -> int:
    score = prediction.probability
    if score is None:
        score = prediction.prediction
    return int(score >= threshold)


def _findings(
    total_return: float,
    baseline_return: float,
    skipped: int,
    prediction_count: int,
) -> tuple[str, ...]:
    findings: list[str] = []
    if total_return <= baseline_return:
        findings.append("Model-derived research signals did not outperform buy-and-hold.")
    if skipped:
        findings.append(
            f"{skipped} of {prediction_count} retained test predictions lacked an eligible execution bar."
        )
    return tuple(findings)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode()
    return hashlib.sha256(encoded).hexdigest()
