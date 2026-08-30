"""Semantic desktop API for D9 forward paper evaluation and simulated orders."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from pydantic import ValidationError

from osca.desktop_api.portfolio_accounting import (
    _allowed,
    _optional_datetime,
    _optional_decimal_or_none,
    _optional_lot_allocations,
    _optional_text_or_none,
    _required_datetime,
    _required_decimal,
    _required_path,
    _required_text,
    _required_uuid,
)
from osca.desktop_api.portfolio_analytics import PortfolioAnalyticsDesktopService
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.service import DesktopServiceError
from osca.paper.contracts import HealthGateStatus
from osca.paper.forward_comparison import ComparisonMetric, build_forward_backtest_comparison
from osca.paper.forward_evidence import ForwardEvidenceError, append_completed_bar_mark
from osca.paper.forward_service import ForwardPaperError, ForwardPaperService
from osca.paper.order_contracts import (
    ExecutionAssumptions,
    OrderSide,
    OrderSourceKind,
    PaperMarketBar,
    SimulatedOrderDraft,
    SimulatedOrderType,
)
from osca.paper.order_persistence import (
    OrderConflictError,
    OrderNotFoundError,
    OrderPersistenceError,
)
from osca.paper.services import decide_paper_control, evaluate_paper_health_gate


class PaperForwardDesktopService(PortfolioAnalyticsDesktopService):
    """Extend the D8 desktop composition with local-only D9 paper methods."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._handlers.update(
            {
                "paper.run.bind": self._run_bind,
                "paper.run.inspect": self._run_inspect,
                "paper.assumptions.retain": self._assumptions_retain,
                "paper.order.draft.retain": self._draft_retain,
                "paper.order.confirm": self._order_confirm,
                "paper.order.cancel": self._order_cancel,
                "paper.order.process_bar": self._order_process_bar,
                "paper.mark.append": self._mark_append,
                "paper.checkpoint.record": self._checkpoint_record,
                "paper.comparison.build": self._comparison_build,
            }
        )

    def _run_bind(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "paper_run_id",
                "paper_account_id",
                "portfolio_id",
                "approved_candidate_id",
                "created_at",
            },
            "paper.run.bind",
        )
        profile_root = _required_path(params, "profile_root")
        service = _paper_service(profile_root)
        with ProfileMutationLock(profile_root):
            binding = _paper_call(
                lambda: service.bind_run(
                    paper_run_id=_required_uuid(params, "paper_run_id"),
                    paper_account_id=_required_uuid(params, "paper_account_id"),
                    portfolio_id=_required_uuid(params, "portfolio_id"),
                    approved_candidate_id=_optional_uuid(params, "approved_candidate_id"),
                    created_at=_optional_datetime(params, "created_at"),
                )
            )
        return _safe_result("osca.desktop-paper-run-bind.result", binding=binding)

    def _run_inspect(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "paper_run_id"}, "paper.run.inspect")
        service = _paper_service(_required_path(params, "profile_root"))
        run_id = _required_uuid(params, "paper_run_id")
        binding = _paper_call(lambda: service.store.get_binding(run_id))
        drafts = _paper_call(lambda: service.store.list_drafts(run_id))
        orders = _paper_call(lambda: service.store.list_orders(run_id))
        order_rows: list[dict[str, Any]] = []
        for order in orders:
            order_rows.append(
                {
                    "order": order.model_dump(mode="json"),
                    "status": service.current_status(order.order_id).value,
                    "remaining_quantity": str(service.remaining_quantity(order.order_id)),
                    "lifecycle": [
                        item.model_dump(mode="json")
                        for item in service.store.list_lifecycle(order.order_id)
                    ],
                    "fills": [
                        item.model_dump(mode="json")
                        for item in service.store.list_fills(order.order_id)
                    ],
                }
            )
        checkpoint = _paper_call(lambda: service.store.latest_checkpoint(run_id))
        projection = _paper_call(lambda: service.accounting.project(binding.portfolio_id))
        return _safe_result(
            "osca.desktop-paper-run-inspect.result",
            binding=binding,
            drafts=drafts,
            orders=order_rows,
            checkpoint=checkpoint,
            projection=projection,
        )

    def _assumptions_retain(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "assumption_id",
                "revision",
                "spread_bps",
                "slippage_bps",
                "fee_bps",
                "flat_fee",
                "latency_ms",
                "max_volume_participation",
                "require_volume",
                "max_order_notional",
                "max_position_notional",
                "created_at",
            },
            "paper.assumptions.retain",
        )
        profile_root = _required_path(params, "profile_root")
        service = _paper_service(profile_root)
        assumptions = _model_call(
            lambda: ExecutionAssumptions(
                assumption_id=_required_uuid(params, "assumption_id"),
                revision=_optional_int(params, "revision", 1, minimum=1),
                spread_bps=_optional_decimal(params, "spread_bps", Decimal("0")),
                slippage_bps=_optional_decimal(params, "slippage_bps", Decimal("0")),
                fee_bps=_optional_decimal(params, "fee_bps", Decimal("0")),
                flat_fee=_optional_decimal(params, "flat_fee", Decimal("0")),
                latency_ms=_optional_int(params, "latency_ms", 0, minimum=0),
                max_volume_participation=_optional_decimal(
                    params,
                    "max_volume_participation",
                    Decimal("1"),
                ),
                require_volume=_optional_bool(params, "require_volume", True),
                max_order_notional=_optional_decimal_or_none(params, "max_order_notional"),
                max_position_notional=_optional_decimal_or_none(
                    params,
                    "max_position_notional",
                ),
                created_at=_optional_datetime(params, "created_at") or datetime.now(UTC),
            )
        )
        with ProfileMutationLock(profile_root):
            retained = _paper_call(lambda: service.retain_assumptions(assumptions))
        return _safe_result("osca.desktop-paper-assumptions.result", assumptions=retained)

    def _draft_retain(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "draft_id",
                "draft_version",
                "paper_run_id",
                "paper_account_id",
                "portfolio_id",
                "source_kind",
                "source_id",
                "approved_candidate_id",
                "instrument_id",
                "timeframe",
                "currency",
                "dataset_revision_id",
                "side",
                "order_type",
                "quantity",
                "limit_price",
                "stop_price",
                "scheduled_at",
                "expires_at",
                "assumption_id",
                "lot_allocations",
                "created_at",
            },
            "paper.order.draft.retain",
        )
        profile_root = _required_path(params, "profile_root")
        service = _paper_service(profile_root)
        draft = _draft_from_params(params)
        with ProfileMutationLock(profile_root):
            retained = _paper_call(lambda: service.retain_draft(draft))
        return _safe_result("osca.desktop-paper-order-draft.result", draft=retained)

    def _order_confirm(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "paper_run_id",
                "draft_id",
                "draft_version",
                "confirmed_at",
                "account_paused",
                "kill_switch_engaged",
            },
            "paper.order.confirm",
        )
        profile_root = _required_path(params, "profile_root")
        service = _paper_service(profile_root)
        run_id = _required_uuid(params, "paper_run_id")
        draft_id = _required_uuid(params, "draft_id")
        draft_version = _optional_int(params, "draft_version", 1, minimum=1)
        draft = next(
            (
                item
                for item in _paper_call(lambda: service.store.list_drafts(run_id))
                if item.draft_id == draft_id and item.draft_version == draft_version
            ),
            None,
        )
        if draft is None:
            raise DesktopServiceError(
                "paper_not_found",
                "retained simulated-order draft was not found",
            )
        control = decide_paper_control(
            paper_account_id=draft.paper_account_id,
            account_paused=_optional_bool(params, "account_paused", False),
            kill_switch_engaged=_optional_bool(params, "kill_switch_engaged", False),
        )
        with ProfileMutationLock(profile_root):
            result = _paper_call(
                lambda: service.confirm_draft(
                    draft,
                    confirmed_at=_required_datetime(params, "confirmed_at"),
                    control_decision=control,
                )
            )
        return _safe_result(
            "osca.desktop-paper-order-confirm.result",
            confirmation=result.confirmation,
            order=result.order,
            risk_decision=result.risk_decision,
            lifecycle=result.lifecycle,
            simulated_only=True,
        )

    def _order_cancel(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "order_id", "source_id", "reason", "effective_at"},
            "paper.order.cancel",
        )
        profile_root = _required_path(params, "profile_root")
        service = _paper_service(profile_root)
        with ProfileMutationLock(profile_root):
            event = _paper_call(
                lambda: service.cancel_order(
                    _required_uuid(params, "order_id"),
                    source_id=_required_text(params, "source_id", limit=200),
                    reason=_required_text(params, "reason", limit=500),
                    effective_at=_optional_datetime(params, "effective_at"),
                )
            )
        return _safe_result("osca.desktop-paper-order-cancel.result", lifecycle_event=event)

    def _order_process_bar(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            _BAR_FIELDS
            | {
                "profile_root",
                "order_id",
                "paper_account_id",
                "paper_run_id",
                "account_paused",
                "kill_switch_engaged",
                "data_status",
                "operational_status",
            },
            "paper.order.process_bar",
        )
        profile_root = _required_path(params, "profile_root")
        service = _paper_service(profile_root)
        control = decide_paper_control(
            paper_account_id=_required_uuid(params, "paper_account_id"),
            account_paused=_optional_bool(params, "account_paused", False),
            kill_switch_engaged=_optional_bool(params, "kill_switch_engaged", False),
        )
        health = evaluate_paper_health_gate(
            paper_run_id=_required_uuid(params, "paper_run_id"),
            data_status=_health_status(params, "data_status"),
            operational_status=_health_status(params, "operational_status"),
        )
        market_bar = _bar_from_params(params)
        with ProfileMutationLock(profile_root):
            result = _paper_call(
                lambda: service.process_bar(
                    _required_uuid(params, "order_id"),
                    market_bar,
                    control_decision=control,
                    health_gate=health,
                )
            )
        return _safe_result("osca.desktop-paper-forward-step.result", step=result)

    def _mark_append(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            _BAR_FIELDS
            | {
                "profile_root",
                "portfolio_id",
                "price_currency",
                "fx_rate_to_base",
                "fx_source",
                "fx_effective_at",
            },
            "paper.mark.append",
        )
        profile_root = _required_path(params, "profile_root")
        service = _paper_service(profile_root)
        market_bar = _bar_from_params(params)
        with ProfileMutationLock(profile_root):
            observation = _paper_call(
                lambda: append_completed_bar_mark(
                    service.accounting,
                    portfolio_id=_required_uuid(params, "portfolio_id"),
                    market_bar=market_bar,
                    price_currency=_required_text(params, "price_currency", limit=3),
                    fx_rate_to_base=_optional_decimal_or_none(params, "fx_rate_to_base"),
                    fx_source=_optional_text_or_none(params, "fx_source", limit=200),
                    fx_effective_at=_optional_datetime(params, "fx_effective_at"),
                )
            )
        return _safe_result("osca.desktop-paper-mark.result", valuation=observation)

    def _checkpoint_record(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "paper_run_id",
                "idempotency_key",
                "last_processed_at",
                "source_event_ids",
            },
            "paper.checkpoint.record",
        )
        profile_root = _required_path(params, "profile_root")
        service = _paper_service(profile_root)
        source_ids = _uuid_list(params, "source_event_ids")
        with ProfileMutationLock(profile_root):
            checkpoint = _paper_call(
                lambda: service.checkpoint_run(
                    _required_uuid(params, "paper_run_id"),
                    idempotency_key=_required_text(params, "idempotency_key", limit=200),
                    last_processed_at=_required_datetime(params, "last_processed_at"),
                    source_event_ids=source_ids,
                )
            )
        return _safe_result("osca.desktop-paper-checkpoint.result", checkpoint=checkpoint)

    def _comparison_build(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "backtest_result_id",
                "paper_run_id",
                "strategy_version_id",
                "assumption_id",
                "backtest_started_at",
                "backtest_ended_at",
                "forward_started_at",
                "forward_ended_at",
                "metrics",
                "methodology_differences",
                "compared_at",
            },
            "paper.comparison.build",
        )
        _required_path(params, "profile_root")
        comparison = _model_call(
            lambda: build_forward_backtest_comparison(
                backtest_result_id=_required_positive_int(params, "backtest_result_id"),
                paper_run_id=_required_uuid(params, "paper_run_id"),
                strategy_version_id=_required_positive_int(params, "strategy_version_id"),
                assumption_id=_required_uuid(params, "assumption_id"),
                backtest_started_at=_required_datetime(params, "backtest_started_at"),
                backtest_ended_at=_required_datetime(params, "backtest_ended_at"),
                forward_started_at=_required_datetime(params, "forward_started_at"),
                forward_ended_at=_required_datetime(params, "forward_ended_at"),
                metrics=_comparison_metrics(params),
                methodology_differences=_text_list(params, "methodology_differences", 500),
                compared_at=_required_datetime(params, "compared_at"),
            )
        )
        return _safe_result(
            "osca.desktop-paper-comparison.result",
            comparison=comparison,
            descriptive_only=True,
        )


_BAR_FIELDS = {
    "evidence_id",
    "instrument_id",
    "dataset_revision_id",
    "market_source_id",
    "timeframe",
    "bar_started_at",
    "bar_ended_at",
    "available_at",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "complete",
    "market_calendar_id",
    "session_open",
}


def _paper_service(profile_root: Path) -> ForwardPaperService:
    if not profile_root.is_dir():
        raise DesktopServiceError(
            "profile_not_found",
            f"profile directory does not exist: {profile_root}",
        )
    return _paper_call(lambda: ForwardPaperService.for_profile(profile_root))


def _paper_call[T](operation: Callable[[], T]) -> T:
    try:
        return operation()
    except OrderConflictError as exc:
        raise DesktopServiceError("paper_conflict", str(exc)) from exc
    except OrderNotFoundError as exc:
        raise DesktopServiceError("paper_not_found", str(exc)) from exc
    except (OrderPersistenceError, ForwardPaperError, ForwardEvidenceError) as exc:
        raise DesktopServiceError("paper_error", str(exc)) from exc
    except ValidationError as exc:
        raise DesktopServiceError("invalid_parameters", str(exc)) from exc


def _model_call[T](operation: Callable[[], T]) -> T:
    try:
        return operation()
    except (ValidationError, ValueError) as exc:
        raise DesktopServiceError("invalid_parameters", str(exc)) from exc


def _draft_from_params(params: dict[str, Any]) -> SimulatedOrderDraft:
    try:
        source_kind = OrderSourceKind(_required_text(params, "source_kind", limit=40))
        side = OrderSide(_required_text(params, "side", limit=10))
        order_type = SimulatedOrderType(_required_text(params, "order_type", limit=40))
    except ValueError as exc:
        raise DesktopServiceError("invalid_parameters", str(exc)) from exc
    return _model_call(
        lambda: SimulatedOrderDraft(
            draft_id=_required_uuid(params, "draft_id"),
            draft_version=_optional_int(params, "draft_version", 1, minimum=1),
            paper_run_id=_required_uuid(params, "paper_run_id"),
            paper_account_id=_required_uuid(params, "paper_account_id"),
            portfolio_id=_required_uuid(params, "portfolio_id"),
            source_kind=source_kind,
            source_id=_required_text(params, "source_id", limit=200),
            approved_candidate_id=_optional_uuid(params, "approved_candidate_id"),
            instrument_id=_required_text(params, "instrument_id", limit=200),
            timeframe=_required_text(params, "timeframe", limit=40),
            currency=_required_text(params, "currency", limit=3),
            dataset_revision_id=_optional_uuid(params, "dataset_revision_id"),
            side=side,
            order_type=order_type,
            quantity=_required_decimal(params, "quantity"),
            limit_price=_optional_decimal_or_none(params, "limit_price"),
            stop_price=_optional_decimal_or_none(params, "stop_price"),
            scheduled_at=_optional_datetime(params, "scheduled_at"),
            expires_at=_optional_datetime(params, "expires_at"),
            assumption_id=_required_uuid(params, "assumption_id"),
            lot_allocations=_optional_lot_allocations(params) or {},
            created_at=_optional_datetime(params, "created_at") or datetime.now(UTC),
        )
    )


def _bar_from_params(params: dict[str, Any]) -> PaperMarketBar:
    return _model_call(
        lambda: PaperMarketBar(
            evidence_id=_required_uuid(params, "evidence_id"),
            instrument_id=_required_text(params, "instrument_id", limit=200),
            dataset_revision_id=_required_uuid(params, "dataset_revision_id"),
            source_id=_required_text(params, "market_source_id", limit=200),
            timeframe=_required_text(params, "timeframe", limit=40),
            bar_started_at=_required_datetime(params, "bar_started_at"),
            bar_ended_at=_required_datetime(params, "bar_ended_at"),
            available_at=_required_datetime(params, "available_at"),
            open=_required_decimal(params, "open"),
            high=_required_decimal(params, "high"),
            low=_required_decimal(params, "low"),
            close=_required_decimal(params, "close"),
            volume=_optional_decimal_or_none(params, "volume"),
            complete=_optional_bool(params, "complete", True),
            market_calendar_id=_optional_text_or_none(params, "market_calendar_id", limit=80),
            session_open=_optional_bool(params, "session_open", True),
        )
    )


def _health_status(params: dict[str, Any], name: str) -> HealthGateStatus:
    raw = _required_text(params, name, limit=20)
    try:
        return HealthGateStatus(raw)
    except ValueError as exc:
        raise DesktopServiceError("invalid_parameters", f"{name} is invalid") from exc


def _safe_result(family: str, **values: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "family": family,
        "version": "1.0.0",
        "network_access_enabled": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "autonomous_execution_enabled": False,
        "live_order_execution": False,
        "real_capital_execution_enabled": False,
    }
    for key, value in values.items():
        if hasattr(value, "model_dump"):
            result[key] = value.model_dump(mode="json")
        elif isinstance(value, tuple):
            result[key] = [
                item.model_dump(mode="json") if hasattr(item, "model_dump") else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def _optional_uuid(params: dict[str, Any], name: str) -> UUID | None:
    if name not in params or params[name] is None:
        return None
    return _required_uuid(params, name)


def _optional_decimal(params: dict[str, Any], name: str, default: Decimal) -> Decimal:
    if name not in params or params[name] is None:
        return default
    return _required_decimal(params, name)


def _optional_bool(params: dict[str, Any], name: str, default: bool) -> bool:
    if name not in params or params[name] is None:
        return default
    value = params[name]
    if not isinstance(value, bool):
        raise DesktopServiceError("invalid_parameters", f"{name} must be boolean")
    return value


def _optional_int(
    params: dict[str, Any],
    name: str,
    default: int,
    *,
    minimum: int,
) -> int:
    if name not in params or params[name] is None:
        return default
    value = params[name]
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise DesktopServiceError("invalid_parameters", f"{name} must be an integer >= {minimum}")
    return int(value)


def _required_positive_int(params: dict[str, Any], name: str) -> int:
    if name not in params:
        raise DesktopServiceError("invalid_parameters", f"{name} is required")
    value = params[name]
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise DesktopServiceError("invalid_parameters", f"{name} must be a positive integer")
    return int(value)


def _uuid_list(params: dict[str, Any], name: str) -> tuple[UUID, ...]:
    value = params.get(name)
    if not isinstance(value, list):
        raise DesktopServiceError("invalid_parameters", f"{name} must be an array")
    result: list[UUID] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise DesktopServiceError("invalid_parameters", f"{name}[{index}] must be a UUID")
        try:
            result.append(UUID(item))
        except ValueError as exc:
            raise DesktopServiceError(
                "invalid_parameters",
                f"{name}[{index}] must be a UUID",
            ) from exc
    return tuple(result)


def _text_list(params: dict[str, Any], name: str, limit: int) -> tuple[str, ...]:
    value = params.get(name)
    if not isinstance(value, list) or not value:
        raise DesktopServiceError("invalid_parameters", f"{name} must be a non-empty array")
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip() or len(item.strip()) > limit:
            raise DesktopServiceError(
                "invalid_parameters",
                f"{name}[{index}] must be non-empty text up to {limit} characters",
            )
        result.append(item.strip())
    return tuple(result)


def _build_comparison_metric(metric_params: dict[str, Any]) -> ComparisonMetric:
    return _model_call(
        lambda: ComparisonMetric(
            name=_required_text(metric_params, "name", limit=200),
            backtest_value=_required_decimal(metric_params, "backtest_value"),
            forward_value=_required_decimal(metric_params, "forward_value"),
            unit=_required_text(metric_params, "unit", limit=80),
            methodology=_required_text(metric_params, "methodology", limit=300),
        )
    )


def _comparison_metrics(params: dict[str, Any]) -> tuple[ComparisonMetric, ...]:
    value = params.get("metrics")
    if not isinstance(value, list) or not value:
        raise DesktopServiceError("invalid_parameters", "metrics must be a non-empty array")
    metrics: list[ComparisonMetric] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise DesktopServiceError("invalid_parameters", f"metrics[{index}] must be an object")
        metrics.append(_build_comparison_metric(dict(item)))
    return tuple(metrics)
