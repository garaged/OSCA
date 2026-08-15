from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

from osca.paper.accounting import PortfolioAccountingError, PortfolioAccountingService
from osca.paper.accounting_contracts import (
    JournalPosting,
    JournalTransaction,
    PostingSide,
    ProjectionHealth,
    ValuationObservation,
)
from osca.paper.accounting_persistence import AccountingConflictError


def at(day: int) -> datetime:
    return datetime(2026, 8, day, 12, tzinfo=UTC)


def service(tmp_path: Path) -> PortfolioAccountingService:
    return PortfolioAccountingService.for_profile(tmp_path)


def test_portfolio_opening_is_decimal_safe_balanced_and_replayable(tmp_path: Path) -> None:
    accounting = service(tmp_path)
    portfolio = accounting.create_portfolio(
        name="Research USD",
        starting_cash="10000.01",
        created_at=at(1),
    )

    projection = accounting.project(portfolio.portfolio_id)
    journal = accounting.journal(portfolio.portfolio_id)

    assert projection.cash_by_currency == {"USD": Decimal("10000.01")}
    assert projection.revision == 1
    assert len(journal) == 1
    assert sum(
        posting.amount if posting.side is PostingSide.DEBIT else -posting.amount
        for posting in journal[0].postings
    ) == Decimal("0")
    with pytest.raises(PortfolioAccountingError, match="binary floats"):
        accounting.create_portfolio(name="Float", starting_cash=100.1)  # type: ignore[arg-type]


def test_journal_contract_rejects_unbalanced_transactions() -> None:
    transaction_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    portfolio_id = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    event_id = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")

    with pytest.raises(ValidationError, match="not balanced"):
        JournalTransaction(
            transaction_id=transaction_id,
            portfolio_id=portfolio_id,
            event_id=event_id,
            effective_at=at(1),
            postings=(
                JournalPosting(
                    posting_id=UUID("11111111-1111-1111-1111-111111111111"),
                    account_code="asset:cash",
                    side=PostingSide.DEBIT,
                    currency="USD",
                    amount=Decimal("10"),
                ),
                JournalPosting(
                    posting_id=UUID("22222222-2222-2222-2222-222222222222"),
                    account_code="equity:funding",
                    side=PostingSide.CREDIT,
                    currency="USD",
                    amount=Decimal("9"),
                ),
            ),
        )


def test_acquisition_disposal_and_fees_rebuild_from_events(tmp_path: Path) -> None:
    accounting = service(tmp_path)
    portfolio = accounting.create_portfolio(name="Lots", starting_cash="5000", created_at=at(1))
    accounting.record_acquisition(
        portfolio.portfolio_id,
        instrument_id="equity:XNAS:AAPL",
        quantity="10",
        unit_price="100",
        fee="1",
        currency="USD",
        effective_at=at(2),
        source_id="buy-1",
    )

    after_buy = accounting.project(portfolio.portfolio_id)
    assert after_buy.cash_by_currency["USD"] == Decimal("3999")
    assert after_buy.positions[0].book_cost == Decimal("1001")
    assert after_buy.fees_by_currency["USD"] == Decimal("1")

    accounting.record_disposal(
        portfolio.portfolio_id,
        instrument_id="equity:XNAS:AAPL",
        quantity="5",
        unit_price="120",
        fee="2",
        currency="USD",
        effective_at=at(3),
        source_id="sell-1",
    )
    after_sell = accounting.project(portfolio.portfolio_id)

    assert after_sell.cash_by_currency["USD"] == Decimal("4597")
    assert after_sell.positions[0].quantity == Decimal("5")
    assert after_sell.positions[0].book_cost == Decimal("500.5")
    assert after_sell.realized_pnl_by_currency["USD"] == Decimal("97.5")
    assert after_sell.fees_by_currency["USD"] == Decimal("3")


def test_ambiguous_multi_lot_disposal_requires_explicit_allocation(tmp_path: Path) -> None:
    accounting = service(tmp_path)
    portfolio = accounting.create_portfolio(name="Explicit lots", starting_cash="5000", created_at=at(1))
    for index, price in enumerate(("100", "110"), start=1):
        accounting.record_acquisition(
            portfolio.portfolio_id,
            instrument_id="AAPL",
            quantity="5",
            unit_price=price,
            currency="USD",
            effective_at=at(index + 1),
            source_id=f"buy-{index}",
        )

    with pytest.raises(PortfolioAccountingError, match="explicit lot allocations"):
        accounting.record_disposal(
            portfolio.portfolio_id,
            instrument_id="AAPL",
            quantity="2",
            unit_price="120",
            currency="USD",
            effective_at=at(4),
            source_id="ambiguous-sell",
        )

    selected = accounting.project(portfolio.portfolio_id).lots[0]
    accounting.record_disposal(
        portfolio.portfolio_id,
        instrument_id="AAPL",
        quantity="2",
        unit_price="120",
        currency="USD",
        lot_allocations={selected.lot_id: "2"},
        effective_at=at(4),
        source_id="allocated-sell",
    )
    remaining = {lot.lot_id: lot.quantity for lot in accounting.project(portfolio.portfolio_id).lots}
    assert remaining[selected.lot_id] == Decimal("3")


def test_split_is_idempotent_by_source_identity(tmp_path: Path) -> None:
    accounting = service(tmp_path)
    portfolio = accounting.create_portfolio(name="Split", starting_cash="5000", created_at=at(1))
    accounting.record_acquisition(
        portfolio.portfolio_id,
        instrument_id="AAPL",
        quantity="5",
        unit_price="100",
        currency="USD",
        effective_at=at(2),
        source_id="buy",
    )

    first = accounting.record_split(
        portfolio.portfolio_id,
        instrument_id="AAPL",
        factor="2",
        effective_at=at(3),
        source_id="split-source",
    )
    second = accounting.record_split(
        portfolio.portfolio_id,
        instrument_id="AAPL",
        factor="2",
        effective_at=at(3),
        source_id="split-source",
    )

    assert first.event_id == second.event_id
    assert accounting.project(portfolio.portfolio_id).positions[0].quantity == Decimal("10")
    assert len(accounting.events(portfolio.portfolio_id)) == 3


def test_source_identity_conflict_fails_closed(tmp_path: Path) -> None:
    accounting = service(tmp_path)
    portfolio = accounting.create_portfolio(name="Conflict", starting_cash="5000", created_at=at(1))
    accounting.record_acquisition(
        portfolio.portfolio_id,
        instrument_id="AAPL",
        quantity="5",
        unit_price="100",
        currency="USD",
        effective_at=at(2),
        source_id="same",
    )

    with pytest.raises(AccountingConflictError, match="different content"):
        accounting.record_acquisition(
            portfolio.portfolio_id,
            instrument_id="AAPL",
            quantity="5",
            unit_price="101",
            currency="USD",
            effective_at=at(2),
            source_id="same",
        )


def test_reversal_compensates_journal_and_excludes_lot_effect(tmp_path: Path) -> None:
    accounting = service(tmp_path)
    portfolio = accounting.create_portfolio(name="Correction", starting_cash="5000", created_at=at(1))
    acquisition = accounting.record_acquisition(
        portfolio.portfolio_id,
        instrument_id="AAPL",
        quantity="5",
        unit_price="100",
        currency="USD",
        effective_at=at(2),
        source_id="bad-buy",
    )

    accounting.reverse_event(
        portfolio.portfolio_id,
        original_event_id=acquisition.event_id,
        reason="fixture correction",
        effective_at=at(3),
        source_id="reverse-bad-buy",
    )
    projection = accounting.project(portfolio.portfolio_id)

    assert projection.cash_by_currency["USD"] == Decimal("5000")
    assert projection.positions == ()
    assert len(accounting.journal(portfolio.portfolio_id)) == 3


def test_fx_cash_and_valuation_provenance_degrade_then_recover(tmp_path: Path) -> None:
    accounting = service(tmp_path)
    portfolio = accounting.create_portfolio(name="FX", starting_cash="5000", created_at=at(1))
    accounting.record_fx_conversion(
        portfolio.portfolio_id,
        from_currency="USD",
        from_amount="1000",
        to_currency="EUR",
        to_amount="900",
        effective_at=at(2),
        source_id="fx-1",
    )
    accounting.record_acquisition(
        portfolio.portfolio_id,
        instrument_id="equity:XETR:SAP",
        quantity="2",
        unit_price="100",
        currency="EUR",
        effective_at=at(3),
        source_id="sap-buy",
    )
    accounting.append_valuation(
        ValuationObservation(
            portfolio_id=portfolio.portfolio_id,
            asset_id="equity:XETR:SAP",
            quantity=Decimal("2"),
            unit_price=Decimal("110"),
            price_currency="EUR",
            price_source="fixture",
            price_effective_at=at(4),
            valuation_revision="sap-r1",
        )
    )

    degraded = accounting.project(portfolio.portfolio_id)
    assert degraded.health is ProjectionHealth.DEGRADED
    assert any("missing FX evidence" in item for item in degraded.missing_evidence)

    accounting.append_valuation(
        ValuationObservation(
            portfolio_id=portfolio.portfolio_id,
            asset_id="equity:XETR:SAP",
            quantity=Decimal("2"),
            unit_price=Decimal("110"),
            price_currency="EUR",
            price_source="fixture",
            price_effective_at=at(4),
            fx_rate_to_base=Decimal("1.1"),
            fx_source="fixture-fx",
            fx_effective_at=at(4),
            valuation_revision="sap-r2",
        )
    )
    accounting.append_valuation(
        ValuationObservation(
            portfolio_id=portfolio.portfolio_id,
            asset_id="currency:EUR",
            quantity=Decimal("700"),
            unit_price=Decimal("1"),
            price_currency="EUR",
            price_source="currency-unit",
            price_effective_at=at(4),
            fx_rate_to_base=Decimal("1.1"),
            fx_source="fixture-fx",
            fx_effective_at=at(4),
            valuation_revision="eur-r1",
        )
    )

    recovered = accounting.project(portfolio.portfolio_id)
    assert recovered.health is ProjectionHealth.HEALTHY
    assert recovered.equity_base == Decimal("5012")
    assert recovered.unrealized_pnl_base == Decimal("22")


def test_fork_moves_explicit_book_cost_without_changing_total(tmp_path: Path) -> None:
    accounting = service(tmp_path)
    portfolio = accounting.create_portfolio(name="Fork", starting_cash="5000", created_at=at(1))
    accounting.record_acquisition(
        portfolio.portfolio_id,
        instrument_id="crypto:BTC",
        quantity="1",
        unit_price="1000",
        currency="USD",
        effective_at=at(2),
        source_id="btc-buy",
    )
    source_lot = accounting.project(portfolio.portfolio_id).lots[0]

    accounting.record_fork(
        portfolio.portfolio_id,
        source_instrument_id="crypto:BTC",
        new_instrument_id="crypto:BCH",
        new_quantity="1",
        currency="USD",
        allocated_book_cost="200",
        source_lot_allocations={source_lot.lot_id: "200"},
        effective_at=at(3),
        source_id="fork-1",
    )
    projection = accounting.project(portfolio.portfolio_id)
    book_costs = {position.instrument_id: position.book_cost for position in projection.positions}

    assert book_costs == {"crypto:BCH": Decimal("200"), "crypto:BTC": Decimal("800")}


def test_append_only_triggers_reject_update_and_delete(tmp_path: Path) -> None:
    import sqlite3

    accounting = service(tmp_path)
    portfolio = accounting.create_portfolio(name="Immutable", starting_cash="100", created_at=at(1))
    database_path = tmp_path / "portfolio-accounting.sqlite"

    with sqlite3.connect(database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE accounting_events SET source_id = 'changed' WHERE portfolio_id = ?",
                (str(portfolio.portfolio_id),),
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "DELETE FROM journal_transactions WHERE portfolio_id = ?",
                (str(portfolio.portfolio_id),),
            )
