from __future__ import annotations

from pathlib import Path
from typing import Any

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.portfolio_analytics import PortfolioAnalyticsDesktopService


def call(
    service: PortfolioAnalyticsDesktopService,
    method: str,
    params: dict[str, Any],
) -> DesktopResponse:
    return service.handle(
        DesktopRequest(
            request_id=f"test-{method}",
            method=method,
            params=params,
        )
    )


def setup_profile(
    tmp_path: Path,
) -> tuple[PortfolioAnalyticsDesktopService, Path, str]:
    service = PortfolioAnalyticsDesktopService(state_root=tmp_path / "state")
    profile_root = tmp_path / "profile"
    created_profile = call(
        service,
        "profile.create",
        {"profile_root": str(profile_root)},
    )
    assert created_profile.status == "ok", created_profile.error
    created = call(
        service,
        "portfolio.create",
        {
            "profile_root": str(profile_root),
            "name": "Analytics",
            "starting_cash": "1000",
        },
    )
    assert created.status == "ok", created.error
    assert created.result is not None
    portfolio_id = str(created.result["portfolio"]["portfolio_id"])
    return service, profile_root, portfolio_id


def test_desktop_captures_snapshots_and_reports_performance(tmp_path: Path) -> None:
    service, profile_root, portfolio_id = setup_profile(tmp_path)

    first = call(
        service,
        "portfolio.analytics.snapshot.capture",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "captured_at": "2026-08-01T12:00:00+00:00",
        },
    )
    assert first.status == "ok", first.error

    acquired = call(
        service,
        "portfolio.acquisition.record",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "instrument_id": "AAPL",
            "quantity": "5",
            "unit_price": "100",
            "currency": "USD",
            "source_id": "buy-1",
        },
    )
    assert acquired.status == "ok", acquired.error
    valuation = call(
        service,
        "portfolio.valuation.record",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "asset_id": "AAPL",
            "quantity": "5",
            "unit_price": "120",
            "price_currency": "USD",
            "price_source": "fixture",
            "price_effective_at": "2026-08-02T12:00:00+00:00",
            "valuation_revision": "aapl-r1",
        },
    )
    assert valuation.status == "ok", valuation.error
    second = call(
        service,
        "portfolio.analytics.snapshot.capture",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "captured_at": "2026-08-02T12:00:00+00:00",
        },
    )
    assert second.status == "ok", second.error

    report = call(
        service,
        "portfolio.analytics.report",
        {"profile_root": str(profile_root), "portfolio_id": portfolio_id},
    )
    assert report.status == "ok", report.error
    assert report.result is not None
    assert report.result["snapshot_count"] == 2
    assert report.result["performance"]["cumulative_return"] == "0.1"
    assert report.result["attribution"]["items"][0]["unrealized_pnl_base"] == "100"
    assert report.result["recommendations_enabled"] is False
    assert report.result["real_capital_execution_enabled"] is False


def test_desktop_scenario_is_hypothetical_and_rejects_float_shocks(tmp_path: Path) -> None:
    service, profile_root, portfolio_id = setup_profile(tmp_path)
    acquired = call(
        service,
        "portfolio.acquisition.record",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "instrument_id": "AAPL",
            "quantity": "5",
            "unit_price": "100",
            "currency": "USD",
            "source_id": "buy-1",
        },
    )
    assert acquired.status == "ok", acquired.error
    valuation = call(
        service,
        "portfolio.valuation.record",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "asset_id": "AAPL",
            "quantity": "5",
            "unit_price": "100",
            "price_currency": "USD",
            "price_source": "fixture",
            "price_effective_at": "2026-08-02T12:00:00+00:00",
            "valuation_revision": "aapl-r1",
        },
    )
    assert valuation.status == "ok", valuation.error

    scenario = call(
        service,
        "portfolio.analytics.scenario",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "asset_shocks": {"AAPL": "0.10"},
        },
    )
    assert scenario.status == "ok", scenario.error
    assert scenario.result is not None
    assert scenario.result["scenario"]["baseline_equity"] == "1000"
    assert scenario.result["scenario"]["scenario_equity"] == "1050.00"
    assert scenario.result["scenario"]["mutated_portfolio"] is False

    invalid = call(
        service,
        "portfolio.analytics.scenario",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "asset_shocks": {"AAPL": 0.1},
        },
    )
    assert invalid.status == "error"
    assert invalid.error is not None
    assert invalid.error.code == "invalid_parameters"


def test_desktop_benchmark_comparison_is_descriptive_only(tmp_path: Path) -> None:
    service, profile_root, portfolio_id = setup_profile(tmp_path)
    first = call(
        service,
        "portfolio.analytics.snapshot.capture",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "captured_at": "2026-08-01T12:00:00+00:00",
        },
    )
    assert first.status == "ok", first.error
    second = call(
        service,
        "portfolio.analytics.snapshot.capture",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "captured_at": "2026-08-02T12:00:00+00:00",
        },
    )
    assert second.status == "ok", second.error

    comparison = call(
        service,
        "portfolio.analytics.benchmark",
        {
            "profile_root": str(profile_root),
            "portfolio_id": portfolio_id,
            "benchmark": [
                {
                    "observed_at": "2026-08-01T12:00:00+00:00",
                    "value": "100",
                    "source_id": "local-benchmark",
                },
                {
                    "observed_at": "2026-08-02T12:00:00+00:00",
                    "value": "105",
                    "source_id": "local-benchmark",
                },
            ],
        },
    )
    assert comparison.status == "ok", comparison.error
    assert comparison.result is not None
    assert comparison.result["comparison"]["portfolio_return"] == "0"
    assert comparison.result["comparison"]["benchmark_return"] == "0.05"
    assert comparison.result["comparison"]["excess_return"] == "-0.05"
    assert comparison.result["descriptive_only"] is True
    assert comparison.result["recommendations_enabled"] is False
