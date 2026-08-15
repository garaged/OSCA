from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from osca.paper.accounting import PortfolioAccountingError, PortfolioAccountingService
from osca.paper.accounting_analytics import (
    BenchmarkObservation,
    PortfolioAnalyticsService,
)
from osca.paper.accounting_contracts import ProjectionHealth, ValuationObservation


def at(day: int) -> datetime:
    return datetime(2026, 8, day, 12, tzinfo=UTC)


def setup_valued_portfolio(
    tmp_path: Path,
) -> tuple[PortfolioAccountingService, PortfolioAnalyticsService, str]:
    accounting = PortfolioAccountingService.for_profile(tmp_path)
    portfolio = accounting.create_portfolio(
        name="Analytics",
        starting_cash="1000",
        created_at=at(1),
    )
    analytics = PortfolioAnalyticsService(accounting)
    analytics.capture_snapshot(portfolio.portfolio_id, captured_at=at(1))
    accounting.record_acquisition(
        portfolio.portfolio_id,
        instrument_id="AAPL",
        quantity="5",
        unit_price="100",
        currency="USD",
        effective_at=at(2),
        source_id="buy-1",
    )
    return accounting, analytics, str(portfolio.portfolio_id)


def record_price(
    accounting: PortfolioAccountingService,
    portfolio_id: str,
    *,
    day: int,
    price: str,
) -> None:
    from uuid import UUID

    accounting.append_valuation(
        ValuationObservation(
            portfolio_id=UUID(portfolio_id),
            asset_id="AAPL",
            quantity=Decimal("5"),
            unit_price=Decimal(price),
            price_currency="USD",
            price_source="fixture",
            price_effective_at=at(day),
            valuation_revision=f"aapl-{day}-{price}",
        )
    )


def test_snapshots_build_performance_drawdown_and_attribution(tmp_path: Path) -> None:
    from uuid import UUID

    accounting, analytics, portfolio_id_text = setup_valued_portfolio(tmp_path)
    portfolio_id = UUID(portfolio_id_text)

    record_price(accounting, portfolio_id_text, day=2, price="100")
    analytics.capture_snapshot(portfolio_id, captured_at=at(2))
    record_price(accounting, portfolio_id_text, day=3, price="120")
    analytics.capture_snapshot(portfolio_id, captured_at=at(3))
    record_price(accounting, portfolio_id_text, day=4, price="80")
    analytics.capture_snapshot(portfolio_id, captured_at=at(4))

    report = analytics.performance_report(portfolio_id)
    assert report.snapshot_count == 4
    assert report.cumulative_return == Decimal("-0.1")
    assert report.max_drawdown == Decimal("900") / Decimal("1100") - Decimal("1")
    assert report.recommendations_enabled is False

    attribution = analytics.attribution_report(portfolio_id)
    assert attribution.health is ProjectionHealth.HEALTHY
    assert len(attribution.items) == 1
    assert attribution.items[0].market_value_base == Decimal("400")
    assert attribution.items[0].book_cost_base == Decimal("500")
    assert attribution.items[0].unrealized_pnl_base == Decimal("-100")
    assert attribution.items[0].allocation == Decimal("1")


def test_snapshot_rejects_degraded_valuation_state(tmp_path: Path) -> None:
    from uuid import UUID

    accounting, analytics, portfolio_id_text = setup_valued_portfolio(tmp_path)
    portfolio_id = UUID(portfolio_id_text)

    assert accounting.project(portfolio_id).health is ProjectionHealth.DEGRADED
    with pytest.raises(PortfolioAccountingError, match="complete valuation evidence"):
        analytics.capture_snapshot(portfolio_id, captured_at=at(2))


def test_scenario_is_non_mutating_and_uses_explicit_shocks(tmp_path: Path) -> None:
    from uuid import UUID

    accounting, analytics, portfolio_id_text = setup_valued_portfolio(tmp_path)
    portfolio_id = UUID(portfolio_id_text)
    record_price(accounting, portfolio_id_text, day=2, price="100")
    baseline = accounting.project(portfolio_id)

    scenario = analytics.scenario_report(
        portfolio_id,
        asset_shocks={"AAPL": Decimal("0.10")},
    )

    assert scenario.baseline_equity == Decimal("1000")
    assert scenario.scenario_equity == Decimal("1050.00")
    assert scenario.equity_change == Decimal("50.00")
    assert scenario.shocked_unrealized_pnl == Decimal("50.00")
    assert scenario.mutated_portfolio is False
    assert accounting.project(portfolio_id) == baseline

    with pytest.raises(PortfolioAccountingError, match="greater than -1"):
        analytics.scenario_report(
            portfolio_id,
            asset_shocks={"AAPL": Decimal("-1")},
        )


def test_benchmark_comparison_is_descriptive_and_provenanced(tmp_path: Path) -> None:
    from uuid import UUID

    accounting, analytics, portfolio_id_text = setup_valued_portfolio(tmp_path)
    portfolio_id = UUID(portfolio_id_text)
    record_price(accounting, portfolio_id_text, day=2, price="100")
    analytics.capture_snapshot(portfolio_id, captured_at=at(2))
    record_price(accounting, portfolio_id_text, day=3, price="120")
    analytics.capture_snapshot(portfolio_id, captured_at=at(3))

    comparison = analytics.benchmark_comparison(
        portfolio_id,
        (
            BenchmarkObservation(observed_at=at(1), value=Decimal("100"), source_id="fixture"),
            BenchmarkObservation(observed_at=at(3), value=Decimal("105"), source_id="fixture"),
        ),
    )

    assert comparison.portfolio_return == Decimal("0.1")
    assert comparison.benchmark_return == Decimal("0.05")
    assert comparison.excess_return == Decimal("0.05")
    assert comparison.benchmark_source_ids == ("fixture",)
    assert comparison.descriptive_only is True
    assert comparison.recommendations_enabled is False


def test_fx_shock_applies_to_non_base_cash_and_positions(tmp_path: Path) -> None:
    from uuid import UUID

    accounting = PortfolioAccountingService.for_profile(tmp_path)
    portfolio = accounting.create_portfolio(
        name="FX analytics",
        starting_cash="1000",
        created_at=at(1),
    )
    accounting.record_fx_conversion(
        portfolio.portfolio_id,
        from_currency="USD",
        from_amount="500",
        to_currency="EUR",
        to_amount="400",
        effective_at=at(2),
        source_id="fx-1",
    )
    accounting.record_acquisition(
        portfolio.portfolio_id,
        instrument_id="SAP",
        quantity="2",
        unit_price="100",
        currency="EUR",
        effective_at=at(3),
        source_id="sap-buy",
    )
    accounting.append_valuation(
        ValuationObservation(
            portfolio_id=portfolio.portfolio_id,
            asset_id="SAP",
            quantity=Decimal("2"),
            unit_price=Decimal("100"),
            price_currency="EUR",
            price_source="fixture",
            price_effective_at=at(4),
            fx_rate_to_base=Decimal("1.25"),
            fx_source="fixture-fx",
            fx_effective_at=at(4),
            valuation_revision="sap-r1",
        )
    )
    accounting.append_valuation(
        ValuationObservation(
            portfolio_id=portfolio.portfolio_id,
            asset_id="currency:EUR",
            quantity=Decimal("200"),
            unit_price=Decimal("1"),
            price_currency="EUR",
            price_source="currency-unit",
            price_effective_at=at(4),
            fx_rate_to_base=Decimal("1.25"),
            fx_source="fixture-fx",
            fx_effective_at=at(4),
            valuation_revision="eur-r1",
        )
    )
    analytics = PortfolioAnalyticsService(accounting)

    baseline = accounting.project(portfolio.portfolio_id)
    assert baseline.equity_base == Decimal("1000")
    scenario = analytics.scenario_report(
        UUID(str(portfolio.portfolio_id)),
        asset_shocks={},
        fx_shocks={"EUR": Decimal("0.10")},
    )
    assert scenario.scenario_equity == Decimal("1050.000")
