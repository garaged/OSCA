"""Governed D9 forward valuation evidence built from completed market bars."""

from __future__ import annotations

from decimal import Decimal
from uuid import NAMESPACE_URL, UUID, uuid5

from osca.paper.accounting import PortfolioAccountingService
from osca.paper.accounting_contracts import ValuationObservation
from osca.paper.order_contracts import PaperMarketBar

_ZERO = Decimal("0")


class ForwardEvidenceError(ValueError):
    """Raised when forward evidence cannot be produced without guessing."""


def append_completed_bar_mark(
    accounting: PortfolioAccountingService,
    *,
    portfolio_id: UUID,
    market_bar: PaperMarketBar,
    price_currency: str,
    fx_rate_to_base: Decimal | None = None,
    fx_source: str | None = None,
    fx_effective_at=None,
) -> ValuationObservation:
    """Retain a replay-safe close mark from one complete governed bar.

    The completed bar close is a valuation observation only; it is never reused
    as a fill price. Missing FX evidence remains explicit so D8 can degrade the
    resulting projection instead of inventing a conversion.
    """
    if not market_bar.complete:
        raise ForwardEvidenceError("incomplete market bar cannot be valuation authority")
    projection = accounting.project(portfolio_id)
    quantity = sum(
        (
            position.quantity
            for position in projection.positions
            if position.instrument_id == market_bar.instrument_id
            and position.currency == price_currency.upper()
        ),
        _ZERO,
    )
    if quantity == _ZERO:
        raise ForwardEvidenceError("no open matching position exists for forward valuation")

    valuation_revision = (
        f"paper-close:{market_bar.dataset_revision_id}:{market_bar.evidence_id}"
    )
    observation_id = uuid5(
        NAMESPACE_URL,
        f"osca-paper-valuation:{portfolio_id}:{market_bar.instrument_id}:{valuation_revision}",
    )
    observation = ValuationObservation(
        observation_id=observation_id,
        portfolio_id=portfolio_id,
        asset_id=market_bar.instrument_id,
        quantity=quantity,
        unit_price=market_bar.close,
        price_currency=price_currency,
        price_source=f"paper-bar:{market_bar.source_id}",
        price_effective_at=market_bar.bar_ended_at,
        fx_rate_to_base=fx_rate_to_base,
        fx_source=fx_source,
        fx_effective_at=fx_effective_at,
        valuation_revision=valuation_revision,
        recorded_at=market_bar.available_at,
    )
    return accounting.append_valuation(observation)
