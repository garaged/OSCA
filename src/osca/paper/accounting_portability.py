"""Non-destructive lifecycle and portable evidence bundles for D8 accounting."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Self
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.paper.accounting import (
    ZERO,
    PortfolioAccountingError,
    PortfolioAccountingService,
    _make_event,
    _posting,
    _transaction,
    _transaction_id,
)
from osca.paper.accounting_contracts import (
    AccountingEvent,
    AccountingEventType,
    JournalPosting,
    JournalTransaction,
    PortfolioProjection,
    PostingSide,
    ValuationObservation,
    VirtualPortfolio,
)
from osca.paper.accounting_persistence import (
    AccountingConflictError,
    SQLitePortfolioAccountingStore,
)


class PortfolioBundle(BaseModel):
    """Portable, digest-protected accounting authority for one portfolio."""

    model_config = ConfigDict(frozen=True)

    family: str = "osca.virtual-portfolio-bundle"
    version: str = "1.0.0"
    portfolio: VirtualPortfolio
    events: tuple[AccountingEvent, ...]
    transactions: tuple[JournalTransaction, ...]
    valuations: tuple[ValuationObservation, ...] = ()
    content_digest: str = Field(min_length=64, max_length=64)

    @model_validator(mode="after")
    def validate_linkage(self) -> Self:
        portfolio_id = self.portfolio.portfolio_id
        if not self.events:
            raise ValueError("portfolio bundle must contain at least one accounting event")
        expected_sequences = tuple(range(1, len(self.events) + 1))
        actual_sequences = tuple(event.sequence for event in self.events)
        if actual_sequences != expected_sequences:
            raise ValueError("portfolio bundle event sequence must be contiguous from 1")
        if any(event.portfolio_id != portfolio_id for event in self.events):
            raise ValueError("portfolio bundle event belongs to another portfolio")
        if any(transaction.portfolio_id != portfolio_id for transaction in self.transactions):
            raise ValueError("portfolio bundle journal belongs to another portfolio")
        if any(observation.portfolio_id != portfolio_id for observation in self.valuations):
            raise ValueError("portfolio bundle valuation belongs to another portfolio")
        event_ids = {event.event_id for event in self.events}
        transaction_event_ids = {transaction.event_id for transaction in self.transactions}
        if len(event_ids) != len(self.events):
            raise ValueError("portfolio bundle contains duplicate event identities")
        if len(transaction_event_ids) != len(self.transactions):
            raise ValueError("portfolio bundle contains duplicate journal event identities")
        if event_ids != transaction_event_ids:
            raise ValueError("portfolio bundle must contain exactly one journal per event")
        if len({item.transaction_id for item in self.transactions}) != len(self.transactions):
            raise ValueError("portfolio bundle contains duplicate transaction identities")
        if len({item.observation_id for item in self.valuations}) != len(self.valuations):
            raise ValueError("portfolio bundle contains duplicate valuation identities")
        return self


def _bundle_payload(
    portfolio: VirtualPortfolio,
    events: tuple[AccountingEvent, ...],
    transactions: tuple[JournalTransaction, ...],
    valuations: tuple[ValuationObservation, ...],
) -> dict[str, object]:
    return {
        "family": "osca.virtual-portfolio-bundle",
        "version": "1.0.0",
        "portfolio": portfolio.model_dump(mode="json"),
        "events": [event.model_dump(mode="json") for event in events],
        "transactions": [item.model_dump(mode="json") for item in transactions],
        "valuations": [item.model_dump(mode="json") for item in valuations],
    }


def bundle_digest(
    portfolio: VirtualPortfolio,
    events: tuple[AccountingEvent, ...],
    transactions: tuple[JournalTransaction, ...],
    valuations: tuple[ValuationObservation, ...],
) -> str:
    canonical = json.dumps(
        _bundle_payload(portfolio, events, transactions, valuations),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def export_portfolio_bundle(
    service: PortfolioAccountingService,
    portfolio_id: UUID,
) -> PortfolioBundle:
    portfolio = service.get_portfolio(portfolio_id)
    events = service.events(portfolio_id)
    transactions = service.journal(portfolio_id)
    valuations = service.valuations(portfolio_id)
    return PortfolioBundle(
        portfolio=portfolio,
        events=events,
        transactions=transactions,
        valuations=valuations,
        content_digest=bundle_digest(portfolio, events, transactions, valuations),
    )


def verify_portfolio_bundle(bundle: PortfolioBundle) -> None:
    expected = bundle_digest(
        bundle.portfolio,
        bundle.events,
        bundle.transactions,
        bundle.valuations,
    )
    if expected != bundle.content_digest:
        raise PortfolioAccountingError("portfolio bundle digest validation failed")


def write_portfolio_bundle(bundle: PortfolioBundle, output_path: Path) -> Path:
    verify_portfolio_bundle(bundle)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(bundle.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return output_path


def read_portfolio_bundle(input_path: Path) -> PortfolioBundle:
    bundle = PortfolioBundle.model_validate_json(input_path.read_text(encoding="utf-8"))
    verify_portfolio_bundle(bundle)
    return bundle


def restore_portfolio_bundle(
    store: SQLitePortfolioAccountingStore,
    bundle: PortfolioBundle,
) -> VirtualPortfolio:
    """Validate first, then restore all authority in one SQLite transaction."""
    verify_portfolio_bundle(bundle)
    store.initialize()
    portfolio = bundle.portfolio
    connection = sqlite3.connect(store.database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """
            INSERT INTO virtual_portfolios(portfolio_id, created_at, payload_json)
            VALUES(?, ?, ?)
            """,
            (
                str(portfolio.portfolio_id),
                portfolio.created_at.isoformat(),
                portfolio.model_dump_json(),
            ),
        )
        for event in bundle.events:
            connection.execute(
                """
                INSERT INTO accounting_events(
                    event_id, portfolio_id, sequence, event_type, source_kind,
                    source_id, content_digest, effective_at, payload_json
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(event.event_id),
                    str(event.portfolio_id),
                    event.sequence,
                    event.event_type.value,
                    event.source_kind,
                    event.source_id,
                    event.content_digest,
                    event.effective_at.isoformat(),
                    event.model_dump_json(),
                ),
            )
        for transaction in bundle.transactions:
            connection.execute(
                """
                INSERT INTO journal_transactions(
                    transaction_id, portfolio_id, event_id, effective_at, payload_json
                ) VALUES(?, ?, ?, ?, ?)
                """,
                (
                    str(transaction.transaction_id),
                    str(transaction.portfolio_id),
                    str(transaction.event_id),
                    transaction.effective_at.isoformat(),
                    transaction.model_dump_json(),
                ),
            )
        for observation in bundle.valuations:
            connection.execute(
                """
                INSERT INTO valuation_observations(
                    observation_id, portfolio_id, asset_id, valuation_revision,
                    price_effective_at, payload_json
                ) VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    str(observation.observation_id),
                    str(observation.portfolio_id),
                    observation.asset_id,
                    observation.valuation_revision,
                    observation.price_effective_at.isoformat(),
                    observation.model_dump_json(),
                ),
            )
        connection.commit()
    except sqlite3.IntegrityError as exc:
        connection.rollback()
        raise AccountingConflictError(
            "portfolio bundle conflicts with retained immutable evidence"
        ) from exc
    finally:
        connection.close()
    return portfolio


def _opening_postings(
    transaction_id: UUID,
    projection: PortfolioProjection,
) -> tuple[JournalPosting, ...]:
    postings: list[JournalPosting] = []
    index = 0
    currencies = set(projection.cash_by_currency)
    currencies.update(lot.currency for lot in projection.lots)
    if not currencies:
        currencies.add(projection.base_currency)
    for currency in sorted(currencies):
        cash = projection.cash_by_currency.get(currency, ZERO)
        book_cost = sum(
            (lot.book_cost for lot in projection.lots if lot.currency == currency),
            ZERO,
        )
        if cash < ZERO or book_cost < ZERO:
            raise PortfolioAccountingError("clone/reset opening state cannot contain negative assets")
        total_assets = cash + book_cost
        if cash != ZERO:
            postings.append(
                _posting(
                    transaction_id,
                    index,
                    "asset:cash",
                    PostingSide.DEBIT,
                    currency,
                    cash,
                )
            )
            index += 1
        if book_cost != ZERO:
            postings.append(
                _posting(
                    transaction_id,
                    index,
                    "asset:investment-book",
                    PostingSide.DEBIT,
                    currency,
                    book_cost,
                )
            )
            index += 1
        if total_assets != ZERO:
            postings.append(
                _posting(
                    transaction_id,
                    index,
                    "equity:opening-state",
                    PostingSide.CREDIT,
                    currency,
                    total_assets,
                )
            )
            index += 1
    if len(postings) < 2:
        postings.extend(
            (
                _posting(
                    transaction_id,
                    index,
                    "memo:opening-state",
                    PostingSide.DEBIT,
                    projection.base_currency,
                    ZERO,
                ),
                _posting(
                    transaction_id,
                    index + 1,
                    "memo:opening-state",
                    PostingSide.CREDIT,
                    projection.base_currency,
                    ZERO,
                ),
            )
        )
    return tuple(postings)


def _opening_snapshot(
    service: PortfolioAccountingService,
    source_portfolio_id: UUID,
    *,
    name: str,
    lineage_kind: str,
    event_type: AccountingEventType,
    projection: PortfolioProjection,
    created_at: datetime | None,
) -> VirtualPortfolio:
    source = service.get_portfolio(source_portfolio_id)
    timestamp = created_at or datetime.now(UTC)
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise PortfolioAccountingError("created_at must be timezone-aware")
    portfolio = VirtualPortfolio(
        name=name,
        base_currency=source.base_currency,
        created_at=timestamp,
        source_portfolio_id=source_portfolio_id,
        source_revision=projection.revision,
        lineage_kind=lineage_kind,
    )
    opening_lots = [
        {
            "lot_id": str(
                uuid5(
                    NAMESPACE_URL,
                    f"osca-opening-lot:{portfolio.portfolio_id}:{lot.lot_id}",
                )
            ),
            "instrument_id": lot.instrument_id,
            "acquired_at": lot.acquired_at.isoformat(),
            "quantity": str(lot.quantity),
            "book_cost": str(lot.book_cost),
            "currency": lot.currency,
            "source_lot_id": str(lot.lot_id),
        }
        for lot in projection.lots
    ]
    payload = {
        "source_portfolio_id": str(source_portfolio_id),
        "source_revision": str(projection.revision),
        "cash_json": json.dumps(
            {currency: str(amount) for currency, amount in projection.cash_by_currency.items()},
            sort_keys=True,
            separators=(",", ":"),
        ),
        "lots_json": json.dumps(opening_lots, sort_keys=True, separators=(",", ":")),
    }
    event = _make_event(
        portfolio_id=portfolio.portfolio_id,
        sequence=1,
        event_type=event_type,
        effective_at=timestamp,
        source_kind=f"portfolio.{lineage_kind}",
        source_id=str(uuid4()),
        payload=payload,
        recorded_at=timestamp,
    )
    transaction_id = _transaction_id(event.event_id)
    transaction = _transaction(event, _opening_postings(transaction_id, projection))
    service.store.create_portfolio(portfolio, event, transaction)
    return portfolio


def clone_portfolio(
    service: PortfolioAccountingService,
    source_portfolio_id: UUID,
    *,
    name: str,
    created_at: datetime | None = None,
) -> VirtualPortfolio:
    projection = service.project(source_portfolio_id)
    return _opening_snapshot(
        service,
        source_portfolio_id,
        name=name,
        lineage_kind="clone_of",
        event_type=AccountingEventType.CLONE_OPENING,
        projection=projection,
        created_at=created_at,
    )


def reset_portfolio(
    service: PortfolioAccountingService,
    source_portfolio_id: UUID,
    *,
    name: str,
    starting_cash: Decimal | str | int = Decimal("10000"),
    created_at: datetime | None = None,
) -> VirtualPortfolio:
    source = service.get_portfolio(source_portfolio_id)
    amount = Decimal(str(starting_cash).strip())
    if not amount.is_finite() or amount < ZERO:
        raise PortfolioAccountingError("starting_cash must be a finite non-negative decimal")
    projection = PortfolioProjection(
        portfolio_id=source_portfolio_id,
        revision=len(service.events(source_portfolio_id)),
        base_currency=source.base_currency,
        cash_by_currency={source.base_currency: amount},
        positions=(),
        lots=(),
        realized_pnl_by_currency={},
        income_by_currency={},
        fees_by_currency={},
        health="healthy",
    )
    return _opening_snapshot(
        service,
        source_portfolio_id,
        name=name,
        lineage_kind="reset_of",
        event_type=AccountingEventType.RESET_OPENING,
        projection=projection,
        created_at=created_at,
    )
