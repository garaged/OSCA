"""Desktop methods for D8 performance, attribution, benchmark, and scenarios."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from osca.desktop_api.portfolio_accounting import (
    PortfolioAccountingDesktopService,
    _accounting_service,
    _required_path,
    _required_uuid,
)
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.service import DesktopServiceError
from osca.paper.accounting import PortfolioAccountingError
from osca.paper.accounting_analytics import (
    BenchmarkObservation,
    PortfolioAnalyticsService,
)


class PortfolioAnalyticsDesktopService(PortfolioAccountingDesktopService):
    """Add read-mostly D8 analytical evidence methods to Portfolio Lab."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._handlers.update(
            {
                "portfolio.analytics.snapshot.capture": self._snapshot_capture,
                "portfolio.analytics.report": self._analytics_report,
                "portfolio.analytics.scenario": self._scenario_report,
                "portfolio.analytics.benchmark": self._benchmark_comparison,
            }
        )

    def _snapshot_capture(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "portfolio_id", "captured_at"},
            "portfolio.analytics.snapshot.capture",
        )
        profile_root = _required_path(params, "profile_root")
        portfolio_id = _required_uuid(params, "portfolio_id")
        analytics = PortfolioAnalyticsService(_accounting_service(profile_root))
        captured_at = _optional_datetime(params, "captured_at")
        with ProfileMutationLock(profile_root):
            snapshot = _analytics_call(
                lambda: analytics.capture_snapshot(
                    portfolio_id,
                    captured_at=captured_at,
                )
            )
        return {
            "family": "osca.desktop-portfolio-analytics-snapshot.result",
            "version": "1.0.0",
            "snapshot": snapshot.model_dump(mode="json"),
            "network_access_enabled": False,
            "recommendations_enabled": False,
            "real_capital_execution_enabled": False,
        }

    def _analytics_report(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "portfolio_id"},
            "portfolio.analytics.report",
        )
        analytics, portfolio_id = _analytics_context(params)
        snapshots = analytics.list_snapshots(portfolio_id)
        performance = (
            _analytics_call(lambda: analytics.performance_report(portfolio_id))
            if snapshots
            else None
        )
        attribution = _analytics_call(
            lambda: analytics.attribution_report(portfolio_id)
        )
        return {
            "family": "osca.desktop-portfolio-analytics.result",
            "version": "1.0.0",
            "snapshot_count": len(snapshots),
            "performance": (
                performance.model_dump(mode="json") if performance is not None else None
            ),
            "attribution": attribution.model_dump(mode="json"),
            "network_access_enabled": False,
            "recommendations_enabled": False,
            "real_capital_execution_enabled": False,
        }

    def _scenario_report(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "portfolio_id", "asset_shocks", "fx_shocks"},
            "portfolio.analytics.scenario",
        )
        analytics, portfolio_id = _analytics_context(params)
        scenario = _analytics_call(
            lambda: analytics.scenario_report(
                portfolio_id,
                asset_shocks=_shock_map(params.get("asset_shocks"), "asset_shocks"),
                fx_shocks=_shock_map(params.get("fx_shocks"), "fx_shocks"),
            )
        )
        return {
            "family": "osca.desktop-portfolio-scenario.result",
            "version": "1.0.0",
            "scenario": scenario.model_dump(mode="json"),
            "network_access_enabled": False,
            "recommendations_enabled": False,
            "real_capital_execution_enabled": False,
        }

    def _benchmark_comparison(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "portfolio_id", "benchmark"},
            "portfolio.analytics.benchmark",
        )
        analytics, portfolio_id = _analytics_context(params)
        benchmark = _benchmark_points(params.get("benchmark"))
        comparison = _analytics_call(
            lambda: analytics.benchmark_comparison(portfolio_id, benchmark)
        )
        return {
            "family": "osca.desktop-portfolio-benchmark.result",
            "version": "1.0.0",
            "comparison": comparison.model_dump(mode="json"),
            "descriptive_only": True,
            "network_access_enabled": False,
            "recommendations_enabled": False,
            "real_capital_execution_enabled": False,
        }


def _analytics_context(
    params: dict[str, Any],
) -> tuple[PortfolioAnalyticsService, UUID]:
    profile_root = _required_path(params, "profile_root")
    portfolio_id = _required_uuid(params, "portfolio_id")
    return PortfolioAnalyticsService(_accounting_service(profile_root)), portfolio_id


def _allowed(params: dict[str, Any], allowed: set[str], method: str) -> None:
    unexpected = sorted(set(params) - allowed)
    if unexpected:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{method} received unsupported parameters: {', '.join(unexpected)}",
        )


def _analytics_call[T](operation: Any) -> T:
    try:
        result: T = operation()
        return result
    except PortfolioAccountingError as exc:
        raise DesktopServiceError("portfolio_analytics_error", str(exc)) from exc


def _optional_datetime(params: dict[str, Any], name: str) -> datetime | None:
    raw = params.get(name)
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise DesktopServiceError("invalid_parameters", f"{name} must be ISO-8601 text")
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DesktopServiceError("invalid_parameters", f"{name} must be ISO-8601") from exc
    if value.tzinfo is None or value.utcoffset() is None:
        raise DesktopServiceError("invalid_parameters", f"{name} must include a timezone")
    return value


def _shock_map(value: object, name: str) -> dict[str, Decimal]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise DesktopServiceError("invalid_parameters", f"{name} must be an object")
    result: dict[str, Decimal] = {}
    for raw_key, raw_value in value.items():
        if not isinstance(raw_key, str) or not raw_key.strip():
            raise DesktopServiceError(
                "invalid_parameters",
                f"{name} keys must be non-empty strings",
            )
        result[raw_key.strip()] = _exact_decimal(raw_value, f"{name}.{raw_key}")
    return result


def _benchmark_points(value: object) -> tuple[BenchmarkObservation, ...]:
    if not isinstance(value, list):
        raise DesktopServiceError("invalid_parameters", "benchmark must be an array")
    points: list[BenchmarkObservation] = []
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            raise DesktopServiceError(
                "invalid_parameters",
                f"benchmark[{index}] must be an object",
            )
        observed_at = _required_datetime_value(raw.get("observed_at"), index)
        source_id = raw.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise DesktopServiceError(
                "invalid_parameters",
                f"benchmark[{index}].source_id must be non-empty text",
            )
        points.append(
            BenchmarkObservation(
                observed_at=observed_at,
                value=_exact_decimal(raw.get("value"), f"benchmark[{index}].value"),
                source_id=source_id.strip(),
            )
        )
    return tuple(points)


def _required_datetime_value(value: object, index: int) -> datetime:
    if not isinstance(value, str):
        raise DesktopServiceError(
            "invalid_parameters",
            f"benchmark[{index}].observed_at must be ISO-8601 text",
        )
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DesktopServiceError(
            "invalid_parameters",
            f"benchmark[{index}].observed_at must be ISO-8601",
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DesktopServiceError(
            "invalid_parameters",
            f"benchmark[{index}].observed_at must include a timezone",
        )
    return parsed


def _exact_decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise DesktopServiceError(
            "invalid_parameters",
            f"{name} must be an exact decimal string or integer",
        )
    try:
        result = Decimal(str(value).strip())
    except Exception as exc:
        raise DesktopServiceError("invalid_parameters", f"{name} is not a decimal") from exc
    if not result.is_finite():
        raise DesktopServiceError("invalid_parameters", f"{name} must be finite")
    return result
