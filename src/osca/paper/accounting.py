"""Authoritative D8 virtual-portfolio accounting services and deterministic replay."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

from osca.paper.accounting_contracts import (
    AccountingEvent,
    AccountingEventType,
    JournalPosting,
    JournalTransaction,
    LotState,
    PortfolioProjection,
    PositionState,
    PostingSide,
    ProjectionHealth,
    ValuationObservation,
    VirtualPortfolio,
)
from osca.paper.accounting_persistence import (
    AccountingNotFoundError,
    SQLitePortfolioAccountingStore,
)

ZERO = Decimal("0")
ONE = Decimal("1")


class PortfolioAccountingError(ValueError):
    """Raised when an accounting command would violate D8 invariants."""


@dataclass
class _MutableLot:
    lot_id: UUID
    instrument_id: str
    acquired_at: datetime
    quantity: Decimal
    book_cost: Decimal
    currency: str


def decimal_value(value: Decimal | str | int) -> Decimal:
    """Normalize supported exact inputs without accepting binary floats."""
    if isinstance(value, bool) or isinstance(value, float):
        raise PortfolioAccountingError("authoritative accounting values must not use binary floats")
    try:
        normalized = value if isinstance(value, Decimal) else Decimal(str(value).strip())
    except Exception as exc:
        raise PortfolioAccountingError("invalid decimal value") from exc
    if not normalized.is_finite():
        raise PortfolioAccountingError("decimal value must be finite")
    return normalized


def _positive(value: Decimal | str | int, name: str) -> Decimal:
    normalized = decimal_value(value)
    if normalized <= ZERO:
        raise PortfolioAccountingError(f"{name} must be greater than zero")
    return normalized


def _non_negative(value: Decimal | str | int, name: str) -> Decimal:
    normalized = decimal_value(value)
    if normalized < ZERO:
        raise PortfolioAccountingError(f"{name} must not be negative")
    return normalized


def _utc(value: datetime | None) -> datetime:
    result = value or datetime.now(UTC)
    if result.tzinfo is None or result.utcoffset() is None:
        raise PortfolioAccountingError("timestamps must be timezone-aware")
    return result


def _currency(value: str) -> str:
    normalized = value.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise PortfolioAccountingError("currency must be a three-letter alphabetic code")
    return normalized


def _text(value: str, name: str, limit: int = 200) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > limit:
        raise PortfolioAccountingError(f"{name} must be between 1 and {limit} characters")
    return normalized


def _digest(
    *,
    portfolio_id: UUID,
    event_type: AccountingEventType,
    effective_at: datetime,
    source_kind: str,
    source_id: str,
    payload: dict[str, str],
) -> str:
    canonical = json.dumps(
        {
            "portfolio_id": str(portfolio_id),
            "event_type": event_type.value,
            "effective_at": effective_at.isoformat(),
            "source_kind": source_kind,
            "source_id": source_id,
            "payload": payload,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _event_id(portfolio_id: UUID, source_kind: str, source_id: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"osca-accounting:{portfolio_id}:{source_kind}:{source_id}")


def _transaction_id(event_id: UUID) -> UUID:
    return uuid5(NAMESPACE_URL, f"osca-accounting-journal:{event_id}")


def _posting_id(transaction_id: UUID, index: int) -> UUID:
    return uuid5(NAMESPACE_URL, f"osca-accounting-posting:{transaction_id}:{index}")


def _lot_id(event_id: UUID, suffix: str = "lot") -> UUID:
    return uuid5(NAMESPACE_URL, f"osca-accounting-lot:{event_id}:{suffix}")


def _posting(
    transaction_id: UUID,
    index: int,
    account_code: str,
    side: PostingSide,
    currency: str,
    amount: Decimal,
    instrument_id: str | None = None,
) -> JournalPosting:
    return JournalPosting(
        posting_id=_posting_id(transaction_id, index),
        account_code=account_code,
        side=side,
        currency=currency,
        amount=amount,
        instrument_id=instrument_id,
    )


def _make_event(
    *,
    portfolio_id: UUID,
    sequence: int,
    event_type: AccountingEventType,
    effective_at: datetime,
    source_kind: str,
    source_id: str,
    payload: dict[str, str],
    recorded_at: datetime | None = None,
) -> AccountingEvent:
    normalized_source_kind = _text(source_kind, "source_kind")
    normalized_source_id = _text(source_id, "source_id")
    timestamp = _utc(effective_at)
    identifier = _event_id(portfolio_id, normalized_source_kind, normalized_source_id)
    return AccountingEvent(
        event_id=identifier,
        portfolio_id=portfolio_id,
        sequence=sequence,
        event_type=event_type,
        effective_at=timestamp,
        recorded_at=_utc(recorded_at),
        source_kind=normalized_source_kind,
        source_id=normalized_source_id,
        payload=payload,
        content_digest=_digest(
            portfolio_id=portfolio_id,
            event_type=event_type,
            effective_at=timestamp,
            source_kind=normalized_source_kind,
            source_id=normalized_source_id,
            payload=payload,
        ),
    )


def _transaction(
    event: AccountingEvent,
    postings: tuple[JournalPosting, ...],
) -> JournalTransaction:
    return JournalTransaction(
        transaction_id=_transaction_id(event.event_id),
        portfolio_id=event.portfolio_id,
        event_id=event.event_id,
        effective_at=event.effective_at,
        postings=postings,
    )


class PortfolioAccountingService:
    """Command/query service backed by an immutable SQLite accounting journal."""

    def __init__(self, store: SQLitePortfolioAccountingStore) -> None:
        self.store = store
        self.store.initialize()

    @classmethod
    def for_profile(cls, profile_root: Path) -> PortfolioAccountingService:
        database_path = profile_root / "portfolio-accounting.sqlite"
        return cls(SQLitePortfolioAccountingStore(database_path))

    def create_portfolio(
        self,
        *,
        name: str,
        base_currency: str = "USD",
        starting_cash: Decimal | str | int = Decimal("10000"),
        created_at: datetime | None = None,
        source_kind: str = "portfolio.create",
        source_id: str | None = None,
    ) -> VirtualPortfolio:
        timestamp = _utc(created_at)
        cash = _non_negative(starting_cash, "starting_cash")
        portfolio = VirtualPortfolio(
            name=name,
            base_currency=_currency(base_currency),
            created_at=timestamp,
        )
        opening_source = source_id or str(portfolio.portfolio_id)
        payload = {
            "amount": str(cash),
            "currency": portfolio.base_currency,
            "reason": "starting_cash",
        }
        event = _make_event(
            portfolio_id=portfolio.portfolio_id,
            sequence=1,
            event_type=AccountingEventType.FUNDING,
            effective_at=timestamp,
            source_kind=source_kind,
            source_id=opening_source,
            payload=payload,
            recorded_at=timestamp,
        )
        transaction_id = _transaction_id(event.event_id)
        transaction = _transaction(
            event,
            (
                _posting(
                    transaction_id,
                    0,
                    "asset:cash",
                    PostingSide.DEBIT,
                    portfolio.base_currency,
                    cash,
                ),
                _posting(
                    transaction_id,
                    1,
                    "equity:funding",
                    PostingSide.CREDIT,
                    portfolio.base_currency,
                    cash,
                ),
            ),
        )
        self.store.create_portfolio(portfolio, event, transaction)
        return portfolio

    def list_portfolios(self) -> tuple[VirtualPortfolio, ...]:
        return self.store.list_portfolios()

    def get_portfolio(self, portfolio_id: UUID) -> VirtualPortfolio:
        return self.store.get_portfolio(portfolio_id)

    def record_acquisition(
        self,
        portfolio_id: UUID,
        *,
        instrument_id: str,
        quantity: Decimal | str | int,
        unit_price: Decimal | str | int,
        currency: str,
        fee: Decimal | str | int = ZERO,
        effective_at: datetime | None = None,
        source_kind: str = "manual.simulated-acquisition",
        source_id: str,
    ) -> AccountingEvent:
        portfolio = self._active_portfolio(portfolio_id)
        instrument = _text(instrument_id, "instrument_id")
        qty = _positive(quantity, "quantity")
        price = _positive(unit_price, "unit_price")
        fee_amount = _non_negative(fee, "fee")
        normalized_currency = _currency(currency)
        gross = qty * price
        required_cash = gross + fee_amount
        projection = self.project(portfolio_id)
        available_cash = projection.cash_by_currency.get(normalized_currency, ZERO)
        if available_cash < required_cash:
            raise PortfolioAccountingError(
                f"insufficient {normalized_currency} cash: need {required_cash}, have {available_cash}"
            )
        sequence = self.store.next_sequence(portfolio_id)
        timestamp = _utc(effective_at)
        temporary_id = _event_id(
            portfolio_id,
            _text(source_kind, "source_kind"),
            _text(source_id, "source_id"),
        )
        lot_id = _lot_id(temporary_id)
        payload = {
            "instrument_id": instrument,
            "quantity": str(qty),
            "unit_price": str(price),
            "currency": normalized_currency,
            "fee": str(fee_amount),
            "book_cost": str(required_cash),
            "lot_id": str(lot_id),
        }
        event = _make_event(
            portfolio_id=portfolio.portfolio_id,
            sequence=sequence,
            event_type=AccountingEventType.ACQUISITION,
            effective_at=timestamp,
            source_kind=source_kind,
            source_id=source_id,
            payload=payload,
        )
        transaction_id = _transaction_id(event.event_id)
        transaction = _transaction(
            event,
            (
                _posting(
                    transaction_id,
                    0,
                    "asset:investment-book",
                    PostingSide.DEBIT,
                    normalized_currency,
                    required_cash,
                    instrument,
                ),
                _posting(
                    transaction_id,
                    1,
                    "asset:cash",
                    PostingSide.CREDIT,
                    normalized_currency,
                    required_cash,
                ),
            ),
        )
        return self.store.append_event(event, transaction)

    def record_disposal(
        self,
        portfolio_id: UUID,
        *,
        instrument_id: str,
        quantity: Decimal | str | int,
        unit_price: Decimal | str | int,
        currency: str,
        fee: Decimal | str | int = ZERO,
        lot_allocations: dict[UUID, Decimal | str | int] | None = None,
        effective_at: datetime | None = None,
        source_kind: str = "manual.simulated-disposal",
        source_id: str,
    ) -> AccountingEvent:
        portfolio = self._active_portfolio(portfolio_id)
        instrument = _text(instrument_id, "instrument_id")
        qty = _positive(quantity, "quantity")
        price = _positive(unit_price, "unit_price")
        fee_amount = _non_negative(fee, "fee")
        normalized_currency = _currency(currency)
        projection = self.project(portfolio_id)
        open_lots = [
            lot
            for lot in projection.lots
            if lot.instrument_id == instrument and lot.quantity > ZERO
        ]
        if not open_lots:
            raise PortfolioAccountingError(f"no open lots exist for {instrument}")
        allocation = self._resolve_allocations(qty, open_lots, lot_allocations)
        allocated_book = ZERO
        payload_allocations: list[dict[str, str]] = []
        lots_by_id = {lot.lot_id: lot for lot in open_lots}
        for lot_id, allocated_quantity in allocation.items():
            lot = lots_by_id.get(lot_id)
            if lot is None:
                raise PortfolioAccountingError(f"unknown open lot {lot_id}")
            if lot.currency != normalized_currency:
                raise PortfolioAccountingError("disposal currency must match allocated lot currency")
            if allocated_quantity > lot.quantity:
                raise PortfolioAccountingError(f"allocation exceeds remaining quantity for lot {lot_id}")
            unit_book_cost = lot.book_cost / lot.quantity
            book_cost = unit_book_cost * allocated_quantity
            allocated_book += book_cost
            payload_allocations.append(
                {
                    "lot_id": str(lot_id),
                    "quantity": str(allocated_quantity),
                    "book_cost": str(book_cost),
                }
            )
        gross = qty * price
        net_cash = gross - fee_amount
        if net_cash < ZERO:
            raise PortfolioAccountingError("fee cannot exceed disposal proceeds")
        realized = gross - allocated_book - fee_amount
        sequence = self.store.next_sequence(portfolio_id)
        timestamp = _utc(effective_at)
        payload = {
            "instrument_id": instrument,
            "quantity": str(qty),
            "unit_price": str(price),
            "currency": normalized_currency,
            "fee": str(fee_amount),
            "allocated_book_cost": str(allocated_book),
            "lot_allocations_json": json.dumps(
                payload_allocations,
                sort_keys=True,
                separators=(",", ":"),
            ),
        }
        event = _make_event(
            portfolio_id=portfolio.portfolio_id,
            sequence=sequence,
            event_type=AccountingEventType.DISPOSAL,
            effective_at=timestamp,
            source_kind=source_kind,
            source_id=source_id,
            payload=payload,
        )
        transaction_id = _transaction_id(event.event_id)
        postings: list[JournalPosting] = [
            _posting(
                transaction_id,
                0,
                "asset:cash",
                PostingSide.DEBIT,
                normalized_currency,
                net_cash,
            ),
            _posting(
                transaction_id,
                1,
                "asset:investment-book",
                PostingSide.CREDIT,
                normalized_currency,
                allocated_book,
                instrument,
            ),
        ]
        if realized > ZERO:
            postings.append(
                _posting(
                    transaction_id,
                    2,
                    "income:realized-pnl",
                    PostingSide.CREDIT,
                    normalized_currency,
                    realized,
                    instrument,
                )
            )
        elif realized < ZERO:
            postings.append(
                _posting(
                    transaction_id,
                    2,
                    "income:realized-pnl",
                    PostingSide.DEBIT,
                    normalized_currency,
                    -realized,
                    instrument,
                )
            )
        transaction = _transaction(event, tuple(postings))
        return self.store.append_event(event, transaction)

    def record_dividend(
        self,
        portfolio_id: UUID,
        *,
        instrument_id: str,
        amount: Decimal | str | int,
        currency: str,
        effective_at: datetime | None = None,
        source_kind: str = "corporate-action.dividend",
        source_id: str,
    ) -> AccountingEvent:
        portfolio = self._active_portfolio(portfolio_id)
        instrument = _text(instrument_id, "instrument_id")
        cash_amount = _positive(amount, "amount")
        normalized_currency = _currency(currency)
        event = _make_event(
            portfolio_id=portfolio.portfolio_id,
            sequence=self.store.next_sequence(portfolio_id),
            event_type=AccountingEventType.DIVIDEND,
            effective_at=_utc(effective_at),
            source_kind=source_kind,
            source_id=source_id,
            payload={
                "instrument_id": instrument,
                "amount": str(cash_amount),
                "currency": normalized_currency,
            },
        )
        transaction_id = _transaction_id(event.event_id)
        return self.store.append_event(
            event,
            _transaction(
                event,
                (
                    _posting(
                        transaction_id,
                        0,
                        "asset:cash",
                        PostingSide.DEBIT,
                        normalized_currency,
                        cash_amount,
                    ),
                    _posting(
                        transaction_id,
                        1,
                        "income:dividend",
                        PostingSide.CREDIT,
                        normalized_currency,
                        cash_amount,
                        instrument,
                    ),
                ),
            ),
        )

    def record_split(
        self,
        portfolio_id: UUID,
        *,
        instrument_id: str,
        factor: Decimal | str | int,
        effective_at: datetime | None = None,
        source_kind: str = "corporate-action.split",
        source_id: str,
    ) -> AccountingEvent:
        portfolio = self._active_portfolio(portfolio_id)
        instrument = _text(instrument_id, "instrument_id")
        normalized_factor = _positive(factor, "factor")
        projection = self.project(portfolio_id)
        position = next(
            (item for item in projection.positions if item.instrument_id == instrument),
            None,
        )
        if position is None or position.quantity <= ZERO:
            raise PortfolioAccountingError(f"no open position exists for {instrument}")
        event = _make_event(
            portfolio_id=portfolio.portfolio_id,
            sequence=self.store.next_sequence(portfolio_id),
            event_type=AccountingEventType.SPLIT,
            effective_at=_utc(effective_at),
            source_kind=source_kind,
            source_id=source_id,
            payload={
                "instrument_id": instrument,
                "factor": str(normalized_factor),
                "currency": position.currency,
            },
        )
        transaction_id = _transaction_id(event.event_id)
        return self.store.append_event(
            event,
            _transaction(
                event,
                (
                    _posting(
                        transaction_id,
                        0,
                        "memo:corporate-action",
                        PostingSide.DEBIT,
                        position.currency,
                        ZERO,
                        instrument,
                    ),
                    _posting(
                        transaction_id,
                        1,
                        "memo:corporate-action",
                        PostingSide.CREDIT,
                        position.currency,
                        ZERO,
                        instrument,
                    ),
                ),
            ),
        )

    def record_fx_conversion(
        self,
        portfolio_id: UUID,
        *,
        from_currency: str,
        from_amount: Decimal | str | int,
        to_currency: str,
        to_amount: Decimal | str | int,
        effective_at: datetime | None = None,
        source_kind: str = "manual.fx-conversion",
        source_id: str,
    ) -> AccountingEvent:
        portfolio = self._active_portfolio(portfolio_id)
        source_currency = _currency(from_currency)
        target_currency = _currency(to_currency)
        if source_currency == target_currency:
            raise PortfolioAccountingError("FX conversion requires two different currencies")
        source_amount = _positive(from_amount, "from_amount")
        target_amount = _positive(to_amount, "to_amount")
        projection = self.project(portfolio_id)
        available = projection.cash_by_currency.get(source_currency, ZERO)
        if available < source_amount:
            raise PortfolioAccountingError(
                f"insufficient {source_currency} cash: need {source_amount}, have {available}"
            )
        event = _make_event(
            portfolio_id=portfolio.portfolio_id,
            sequence=self.store.next_sequence(portfolio_id),
            event_type=AccountingEventType.FX_CONVERSION,
            effective_at=_utc(effective_at),
            source_kind=source_kind,
            source_id=source_id,
            payload={
                "from_currency": source_currency,
                "from_amount": str(source_amount),
                "to_currency": target_currency,
                "to_amount": str(target_amount),
            },
        )
        transaction_id = _transaction_id(event.event_id)
        return self.store.append_event(
            event,
            _transaction(
                event,
                (
                    _posting(
                        transaction_id,
                        0,
                        "clearing:fx",
                        PostingSide.DEBIT,
                        source_currency,
                        source_amount,
                    ),
                    _posting(
                        transaction_id,
                        1,
                        "asset:cash",
                        PostingSide.CREDIT,
                        source_currency,
                        source_amount,
                    ),
                    _posting(
                        transaction_id,
                        2,
                        "asset:cash",
                        PostingSide.DEBIT,
                        target_currency,
                        target_amount,
                    ),
                    _posting(
                        transaction_id,
                        3,
                        "clearing:fx",
                        PostingSide.CREDIT,
                        target_currency,
                        target_amount,
                    ),
                ),
            ),
        )

    def record_fork(
        self,
        portfolio_id: UUID,
        *,
        source_instrument_id: str,
        new_instrument_id: str,
        new_quantity: Decimal | str | int,
        currency: str,
        allocated_book_cost: Decimal | str | int = ZERO,
        source_lot_allocations: dict[UUID, Decimal | str | int] | None = None,
        effective_at: datetime | None = None,
        source_kind: str = "corporate-action.fork",
        source_id: str,
    ) -> AccountingEvent:
        portfolio = self._active_portfolio(portfolio_id)
        source_instrument = _text(source_instrument_id, "source_instrument_id")
        new_instrument = _text(new_instrument_id, "new_instrument_id")
        if source_instrument == new_instrument:
            raise PortfolioAccountingError("fork instruments must differ")
        quantity = _positive(new_quantity, "new_quantity")
        normalized_currency = _currency(currency)
        book_cost = _non_negative(allocated_book_cost, "allocated_book_cost")
        projection = self.project(portfolio_id)
        open_lots = [
            lot
            for lot in projection.lots
            if lot.instrument_id == source_instrument and lot.quantity > ZERO
        ]
        if not open_lots:
            raise PortfolioAccountingError(f"no open lots exist for {source_instrument}")
        allocations: list[dict[str, str]] = []
        if book_cost > ZERO:
            if source_lot_allocations is None:
                if len(open_lots) != 1:
                    raise PortfolioAccountingError(
                        "explicit source lot book-cost allocations are required for this fork"
                    )
                source_lot_allocations = {open_lots[0].lot_id: book_cost}
            allocated_total = ZERO
            lots = {lot.lot_id: lot for lot in open_lots}
            for lot_id, raw_amount in source_lot_allocations.items():
                amount = _non_negative(raw_amount, "source lot book-cost allocation")
                lot = lots.get(lot_id)
                if lot is None:
                    raise PortfolioAccountingError(f"unknown source lot {lot_id}")
                if amount > lot.book_cost:
                    raise PortfolioAccountingError(f"book-cost allocation exceeds lot {lot_id}")
                allocated_total += amount
                allocations.append({"lot_id": str(lot_id), "book_cost": str(amount)})
            if allocated_total != book_cost:
                raise PortfolioAccountingError(
                    "source lot book-cost allocations must equal allocated_book_cost"
                )
        event_identifier = _event_id(
            portfolio_id,
            _text(source_kind, "source_kind"),
            _text(source_id, "source_id"),
        )
        new_lot_id = _lot_id(event_identifier, "fork")
        event = _make_event(
            portfolio_id=portfolio.portfolio_id,
            sequence=self.store.next_sequence(portfolio_id),
            event_type=AccountingEventType.FORK,
            effective_at=_utc(effective_at),
            source_kind=source_kind,
            source_id=source_id,
            payload={
                "source_instrument_id": source_instrument,
                "new_instrument_id": new_instrument,
                "new_quantity": str(quantity),
                "currency": normalized_currency,
                "allocated_book_cost": str(book_cost),
                "source_allocations_json": json.dumps(
                    allocations,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                "new_lot_id": str(new_lot_id),
            },
        )
        transaction_id = _transaction_id(event.event_id)
        return self.store.append_event(
            event,
            _transaction(
                event,
                (
                    _posting(
                        transaction_id,
                        0,
                        "asset:investment-book",
                        PostingSide.DEBIT,
                        normalized_currency,
                        book_cost,
                        new_instrument,
                    ),
                    _posting(
                        transaction_id,
                        1,
                        "asset:investment-book",
                        PostingSide.CREDIT,
                        normalized_currency,
                        book_cost,
                        source_instrument,
                    ),
                ),
            ),
        )

    def reverse_event(
        self,
        portfolio_id: UUID,
        *,
        original_event_id: UUID,
        reason: str,
        effective_at: datetime | None = None,
        source_kind: str = "manual.correction-reversal",
        source_id: str,
    ) -> AccountingEvent:
        portfolio = self._active_portfolio(portfolio_id)
        original = self.store.get_event(original_event_id)
        if original.portfolio_id != portfolio_id:
            raise PortfolioAccountingError("original event belongs to a different portfolio")
        if original.event_type is AccountingEventType.FUNDING and original.sequence == 1:
            raise PortfolioAccountingError("opening funding cannot be reversed; use reset instead")
        events = self.store.list_events(portfolio_id)
        if any(
            event.event_type is AccountingEventType.REVERSAL
            and event.payload.get("original_event_id") == str(original_event_id)
            for event in events
        ):
            raise PortfolioAccountingError("event has already been reversed")
        original_transaction = next(
            (
                transaction
                for transaction in self.store.list_transactions(portfolio_id)
                if transaction.event_id == original_event_id
            ),
            None,
        )
        if original_transaction is None:
            raise AccountingNotFoundError(f"journal for event {original_event_id} was not found")
        event = _make_event(
            portfolio_id=portfolio.portfolio_id,
            sequence=self.store.next_sequence(portfolio_id),
            event_type=AccountingEventType.REVERSAL,
            effective_at=_utc(effective_at),
            source_kind=source_kind,
            source_id=source_id,
            payload={
                "original_event_id": str(original_event_id),
                "reason": _text(reason, "reason", limit=500),
            },
        )
        transaction_id = _transaction_id(event.event_id)
        postings = tuple(
            _posting(
                transaction_id,
                index,
                posting.account_code,
                PostingSide.CREDIT if posting.side is PostingSide.DEBIT else PostingSide.DEBIT,
                posting.currency,
                posting.amount,
                posting.instrument_id,
            )
            for index, posting in enumerate(original_transaction.postings)
        )
        return self.store.append_event(event, _transaction(event, postings))

    def append_valuation(self, observation: ValuationObservation) -> ValuationObservation:
        self.get_portfolio(observation.portfolio_id)
        return self.store.append_valuation(observation)

    def project(self, portfolio_id: UUID) -> PortfolioProjection:
        portfolio = self.get_portfolio(portfolio_id)
        events = self.store.list_events(portfolio_id)
        transactions = self.store.list_transactions(portfolio_id)
        valuations = self.store.list_valuations(portfolio_id)
        reversed_ids = {
            UUID(event.payload["original_event_id"])
            for event in events
            if event.event_type is AccountingEventType.REVERSAL
            and "original_event_id" in event.payload
        }
        cash: defaultdict[str, Decimal] = defaultdict(lambda: ZERO)
        realized: defaultdict[str, Decimal] = defaultdict(lambda: ZERO)
        income: defaultdict[str, Decimal] = defaultdict(lambda: ZERO)
        fees: defaultdict[str, Decimal] = defaultdict(lambda: ZERO)
        for transaction in transactions:
            for posting in transaction.postings:
                signed_asset = posting.amount if posting.side is PostingSide.DEBIT else -posting.amount
                if posting.account_code == "asset:cash":
                    cash[posting.currency] += signed_asset
                elif posting.account_code == "income:realized-pnl":
                    realized[posting.currency] -= signed_asset
                elif posting.account_code.startswith("income:"):
                    income[posting.currency] -= signed_asset

        for event in events:
            if event.event_id in reversed_ids or event.event_type is AccountingEventType.REVERSAL:
                continue
            fee_text = event.payload.get("fee")
            currency_text = event.payload.get("currency")
            if fee_text is not None and currency_text is not None:
                fees[currency_text] += Decimal(fee_text)

        mutable_lots: dict[UUID, _MutableLot] = {}
        for event in events:
            if event.event_id in reversed_ids or event.event_type is AccountingEventType.REVERSAL:
                continue
            payload = event.payload
            if event.event_type is AccountingEventType.ACQUISITION:
                lot_id = UUID(payload["lot_id"])
                mutable_lots[lot_id] = _MutableLot(
                    lot_id=lot_id,
                    instrument_id=payload["instrument_id"],
                    acquired_at=event.effective_at,
                    quantity=Decimal(payload["quantity"]),
                    book_cost=Decimal(payload["book_cost"]),
                    currency=payload["currency"],
                )
            elif event.event_type is AccountingEventType.DISPOSAL:
                allocations = json.loads(payload["lot_allocations_json"])
                if not isinstance(allocations, list):
                    raise PortfolioAccountingError("retained disposal allocations are invalid")
                for allocation in allocations:
                    if not isinstance(allocation, dict):
                        raise PortfolioAccountingError("retained disposal allocation is invalid")
                    lot_id = UUID(str(allocation["lot_id"]))
                    lot = mutable_lots.get(lot_id)
                    if lot is None:
                        raise PortfolioAccountingError(f"replay cannot resolve disposal lot {lot_id}")
                    quantity = Decimal(str(allocation["quantity"]))
                    book_cost = Decimal(str(allocation["book_cost"]))
                    lot.quantity -= quantity
                    lot.book_cost -= book_cost
            elif event.event_type is AccountingEventType.SPLIT:
                instrument = payload["instrument_id"]
                factor = Decimal(payload["factor"])
                for lot in mutable_lots.values():
                    if lot.instrument_id == instrument:
                        lot.quantity *= factor
            elif event.event_type is AccountingEventType.FORK:
                allocations = json.loads(payload["source_allocations_json"])
                if not isinstance(allocations, list):
                    raise PortfolioAccountingError("retained fork allocations are invalid")
                for allocation in allocations:
                    if not isinstance(allocation, dict):
                        raise PortfolioAccountingError("retained fork allocation is invalid")
                    lot_id = UUID(str(allocation["lot_id"]))
                    lot = mutable_lots.get(lot_id)
                    if lot is None:
                        raise PortfolioAccountingError(f"replay cannot resolve fork lot {lot_id}")
                    amount = Decimal(str(allocation["book_cost"]))
                    lot.book_cost -= amount
                new_lot_id = UUID(payload["new_lot_id"])
                mutable_lots[new_lot_id] = _MutableLot(
                    lot_id=new_lot_id,
                    instrument_id=payload["new_instrument_id"],
                    acquired_at=event.effective_at,
                    quantity=Decimal(payload["new_quantity"]),
                    book_cost=Decimal(payload["allocated_book_cost"]),
                    currency=payload["currency"],
                )

        lots = tuple(
            LotState(
                lot_id=lot.lot_id,
                instrument_id=lot.instrument_id,
                acquired_at=lot.acquired_at,
                quantity=lot.quantity,
                book_cost=lot.book_cost,
                currency=lot.currency,
            )
            for lot in sorted(mutable_lots.values(), key=lambda item: str(item.lot_id))
            if lot.quantity > ZERO
        )
        positions_by_key: defaultdict[tuple[str, str], list[Decimal]] = defaultdict(
            lambda: [ZERO, ZERO]
        )
        for lot in lots:
            key = (lot.instrument_id, lot.currency)
            positions_by_key[key][0] += lot.quantity
            positions_by_key[key][1] += lot.book_cost
        positions = tuple(
            PositionState(
                instrument_id=instrument,
                currency=currency,
                quantity=values[0],
                book_cost=values[1],
            )
            for (instrument, currency), values in sorted(positions_by_key.items())
            if values[0] > ZERO
        )

        latest = self._latest_valuations(valuations)
        missing: list[str] = []
        market_value = ZERO
        total_book_base = ZERO
        gross_exposure = ZERO
        net_exposure = ZERO
        allocation_values: dict[str, Decimal] = {}
        for position in positions:
            observation = latest.get(position.instrument_id)
            if observation is None:
                missing.append(f"missing price evidence for {position.instrument_id}")
                continue
            rate = self._valuation_rate(portfolio.base_currency, observation, missing)
            if rate is None:
                continue
            value = position.quantity * observation.unit_price * rate
            book_base = position.book_cost * (
                ONE if position.currency == portfolio.base_currency else rate
            )
            market_value += value
            total_book_base += book_base
            gross_exposure += abs(value)
            net_exposure += value
            allocation_values[position.instrument_id] = value

        cash_base = ZERO
        for currency, amount in cash.items():
            if currency == portfolio.base_currency:
                cash_base += amount
                continue
            observation = latest.get(f"currency:{currency}")
            if observation is None or observation.fx_rate_to_base is None:
                missing.append(f"missing FX evidence for cash currency {currency}")
                continue
            cash_base += amount * observation.fx_rate_to_base

        health = ProjectionHealth.HEALTHY if not missing else ProjectionHealth.DEGRADED
        equity: Decimal | None = None
        unrealized: Decimal | None = None
        allocation: dict[str, Decimal] = {}
        if health is ProjectionHealth.HEALTHY:
            equity = cash_base + market_value
            unrealized = market_value - total_book_base
            if gross_exposure > ZERO:
                allocation = {
                    asset_id: value / gross_exposure
                    for asset_id, value in sorted(allocation_values.items())
                }

        return PortfolioProjection(
            portfolio_id=portfolio_id,
            revision=len(events),
            base_currency=portfolio.base_currency,
            cash_by_currency=dict(sorted(cash.items())),
            positions=positions,
            lots=lots,
            realized_pnl_by_currency=dict(sorted(realized.items())),
            income_by_currency=dict(sorted(income.items())),
            fees_by_currency=dict(sorted(fees.items())),
            health=health,
            missing_evidence=tuple(sorted(set(missing))),
            equity_base=equity,
            unrealized_pnl_base=unrealized,
            gross_exposure_base=gross_exposure if health is ProjectionHealth.HEALTHY else None,
            net_exposure_base=net_exposure if health is ProjectionHealth.HEALTHY else None,
            allocation_by_asset=allocation,
        )

    def journal(self, portfolio_id: UUID) -> tuple[JournalTransaction, ...]:
        return self.store.list_transactions(portfolio_id)

    def events(self, portfolio_id: UUID) -> tuple[AccountingEvent, ...]:
        return self.store.list_events(portfolio_id)

    def valuations(self, portfolio_id: UUID) -> tuple[ValuationObservation, ...]:
        return self.store.list_valuations(portfolio_id)

    def _active_portfolio(self, portfolio_id: UUID) -> VirtualPortfolio:
        portfolio = self.get_portfolio(portfolio_id)
        if portfolio.status.value != "active":
            raise PortfolioAccountingError("portfolio is not active")
        return portfolio

    @staticmethod
    def _resolve_allocations(
        quantity: Decimal,
        open_lots: list[LotState],
        requested: dict[UUID, Decimal | str | int] | None,
    ) -> dict[UUID, Decimal]:
        if requested is None:
            candidates = [lot for lot in open_lots if lot.quantity >= quantity]
            if len(open_lots) == 1 and len(candidates) == 1:
                return {open_lots[0].lot_id: quantity}
            raise PortfolioAccountingError(
                "explicit lot allocations are required when multiple open lots exist"
            )
        normalized = {
            lot_id: _positive(raw_quantity, "lot allocation quantity")
            for lot_id, raw_quantity in requested.items()
        }
        if sum(normalized.values(), ZERO) != quantity:
            raise PortfolioAccountingError("lot allocations must sum exactly to disposal quantity")
        return normalized

    @staticmethod
    def _latest_valuations(
        observations: tuple[ValuationObservation, ...],
    ) -> dict[str, ValuationObservation]:
        latest: dict[str, ValuationObservation] = {}
        for observation in observations:
            current = latest.get(observation.asset_id)
            if current is None or (
                observation.price_effective_at,
                observation.recorded_at,
                str(observation.observation_id),
            ) > (
                current.price_effective_at,
                current.recorded_at,
                str(current.observation_id),
            ):
                latest[observation.asset_id] = observation
        return latest

    @staticmethod
    def _valuation_rate(
        base_currency: str,
        observation: ValuationObservation,
        missing: list[str],
    ) -> Decimal | None:
        if observation.price_currency == base_currency:
            return ONE
        if observation.fx_rate_to_base is None:
            missing.append(
                f"missing FX evidence for {observation.asset_id} "
                f"{observation.price_currency}->{base_currency}"
            )
            return None
        return observation.fx_rate_to_base
