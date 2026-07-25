from osca.backtesting.api import (
    BacktestDataAvailability,
    BacktestExecutionMode,
    BacktestExecutionPlan,
    BacktestFidelityProfile,
    BacktestFindingSeverity,
    BacktestRequest,
    BacktestValidationFinding,
)

_EXPECTED_EXECUTION_MODE: dict[BacktestFidelityProfile, BacktestExecutionMode] = {
    BacktestFidelityProfile.F0_SIGNAL_STUDY: BacktestExecutionMode.SIGNAL_ONLY,
    BacktestFidelityProfile.F1_VECTORIZED_PORTFOLIO: BacktestExecutionMode.VECTORIZED,
    BacktestFidelityProfile.F2_EVENT_DRIVEN_BAR: BacktestExecutionMode.EVENT_DRIVEN,
    BacktestFidelityProfile.F3_FORWARD_PAPER: BacktestExecutionMode.FORWARD_PAPER,
}


def validate_backtest_request(
    request: BacktestRequest,
) -> tuple[BacktestValidationFinding, ...]:
    findings: list[BacktestValidationFinding] = []
    expected_mode = _EXPECTED_EXECUTION_MODE[request.fidelity_profile]
    if request.execution_mode is not expected_mode:
        findings.append(
            BacktestValidationFinding(
                code="execution_mode_mismatch",
                severity=BacktestFindingSeverity.ERROR,
                message=(
                    f"{request.fidelity_profile} requires {expected_mode}, "
                    f"not {request.execution_mode}"
                ),
            )
        )
    if request.data_availability is BacktestDataAvailability.REVISED_AFTER_FACT:
        findings.append(
            BacktestValidationFinding(
                code="lookahead_data",
                severity=BacktestFindingSeverity.ERROR,
                message="backtests must use point-in-time data availability",
            )
        )
    if (
        request.data_availability is BacktestDataAvailability.PROVISIONAL
        and request.fidelity_profile in {
        BacktestFidelityProfile.F2_EVENT_DRIVEN_BAR,
            BacktestFidelityProfile.F3_FORWARD_PAPER,
        }
    ):
        findings.append(
            BacktestValidationFinding(
                code="provisional_execution_data",
                severity=BacktestFindingSeverity.ERROR,
                message="event-driven and forward-paper profiles cannot use provisional data",
            )
        )
    if request.fidelity_profile is BacktestFidelityProfile.F3_FORWARD_PAPER:
        findings.append(
            BacktestValidationFinding(
                code="paper_account_deferred",
                severity=BacktestFindingSeverity.ERROR,
                message="forward paper execution is deferred until paper-account authority exists",
            )
        )
    return tuple(findings)


def plan_backtest_execution(request: BacktestRequest) -> BacktestExecutionPlan:
    findings = validate_backtest_request(request)
    required_checks = [
        "point_in_time_data",
        "dataset_revision_pinning",
        "assumption_set_pinning",
    ]
    if request.fidelity_profile in {
        BacktestFidelityProfile.F2_EVENT_DRIVEN_BAR,
        BacktestFidelityProfile.F3_FORWARD_PAPER,
    }:
        required_checks.extend(
            [
                "event_order_lifecycle",
                "deterministic_risk_policy",
                "portfolio_accounting_boundary",
            ]
        )
    can_execute = not any(
        finding.severity is BacktestFindingSeverity.ERROR for finding in findings
    )
    return BacktestExecutionPlan(
        request_id=request.request_id,
        can_execute=can_execute,
        required_checks=tuple(required_checks),
        findings=findings,
    )
