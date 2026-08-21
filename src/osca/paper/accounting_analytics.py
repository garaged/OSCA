"""Derived D8 portfolio analytics over retained accounting evidence."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from osca.paper.accounting import ONE, ZERO, PortfolioAccountingError, PortfolioAccountingService
from osca.paper.accounting_contracts import (
    PortfolioProjection,
    ProjectionHealth,
    ValuationObservation,
)


class PortfolioAnalyticsSnapshot(BaseModel):
    """Immutable derived snapshot with explicit accounting/valuation provenance."""

    model_config = ConfigDict(frozen=True)

    family: str = "osca.portfolio-analytics-snapshot"
    version: str = "1.0.0"
    snapshot_id: UUID = Field(default_factory=uuid4)
    portfolio_id: UUID
    captured_at: datetime
    portfolio_revision: int = Field(ge=0)
    projection_digest: str = Field(min_length=64, max_length=64)
    valuation_ids: tuple[UUID, ...]
    projection: PortfolioProjection

    @field_validator("captured_at")
    @classmethod
    def validate_captured_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("captured_at must be timezone-aware")
        return value


class PortfolioPerformancePoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    snapshot_id: UUID
    captured_at: datetime
    equity_base: Decimal
    cumulative_return: Decimal
    drawdown: Decimal


class PortfolioPerformanceReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: str = "osca.portfolio-performance-report"
    version: str = "1.0.0"
    portfolio_id: UUID
    base_currency: str
    evidence_start: datetime
    evidence_end: datetime
    snapshot_count: int = Field(ge=1)
    cumulative_return: Decimal
    max_drawdown: Decimal
    points: tuple[PortfolioPerformancePoint, ...]
    recommendations_enabled: bool = False


class PortfolioAttributionItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    instrument_id: str
    market_value_base: Decimal
    book_cost_base: Decimal
    unrealized_pnl_base: Decimal
    allocation: Decimal
    price_source: str
    price_effective_at: datetime
    fx_source: str | None = None
    fx_effective_at: datetime | None = None


class PortfolioAttributionReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: str = "osca.portfolio-attribution-report"
    version: str = "1.0.0"
    portfolio_id: UUID
    base_currency: str
    health: ProjectionHealth
    missing_evidence: tuple[str, ...]
    items: tuple[PortfolioAttributionItem, ...]
    recommendations_enabled: bool = False


class PortfolioScenarioReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: str = "osca.portfolio-scenario-report"
    version: str = "1.0.0"
    portfolio_id: UUID
    base_currency: str
    baseline_equity: Decimal
    scenario_equity: Decimal
    equity_change: Decimal
    shocked_unrealized_pnl: Decimal
    gross_exposure: Decimal
    asset_shocks: dict[str, Decimal]
    fx_shocks: dict[str, Decimal]
    mutated_portfolio: bool = False
    recommendations_enabled: bool = False


class BenchmarkObservation(BaseModel):
    model_config = ConfigDict(frozen=True)

    observed_at: datetime
    value: Decimal = Field(gt=ZERO)
    source_id: str

    @field_validator("observed_at")
    @classmethod
    def validate_observed_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value

    @field_validator("source_id")
    @classmethod
    def validate_source_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized or len(normalized) > 200:
            raise ValueError("source_id must be between 1 and 200 characters")
        return normalized


class PortfolioBenchmarkComparison(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: str = "osca.portfolio-benchmark-comparison"
    version: str = "1.0.0"
    portfolio_id: UUID
    evidence_start: datetime
    evidence_end: datetime
    portfolio_return: Decimal
    benchmark_return: Decimal
    excess_return: Decimal
    benchmark_source_ids: tuple[str, ...]
    descriptive_only: bool = True
    recommendations_enabled: bool = False


class PortfolioAnalyticsStore:
    """Append-only store for regenerable analytical evidence snapshots."""

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS portfolio_analytics_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    portfolio_id TEXT NOT NULL,
                    captured_at TEXT NOT NULL,
                    portfolio_revision INTEGER NOT NULL,
                    projection_digest TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_portfolio_analytics_snapshots
                    ON portfolio_analytics_snapshots(
                        portfolio_id,
                        captured_at,
                        snapshot_id
                    );
                CREATE TRIGGER IF NOT EXISTS portfolio_analytics_snapshots_no_update
                BEFORE UPDATE ON portfolio_analytics_snapshots BEGIN
                    SELECT RAISE(ABORT, 'portfolio analytics snapshots are append-only');
                END;
                CREATE TRIGGER IF NOT EXISTS portfolio_analytics_snapshots_no_delete
                BEFORE DELETE ON portfolio_analytics_snapshots BEGIN
                    SELECT RAISE(ABORT, 'portfolio analytics snapshots are append-only');
                END;
                """
            )

    def append(self, snapshot: PortfolioAnalyticsSnapshot) -> None:
        self.initialize()
        with sqlite3.connect(self.database_path) as connection:
            try:
                connection.execute(
                    """
                    INSERT INTO portfolio_analytics_snapshots(
                        snapshot_id,
                        portfolio_id,
                        captured_at,
                        portfolio_revision,
                        projection_digest,
                        payload_json
                    ) VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(snapshot.snapshot_id),
                        str(snapshot.portfolio_id),
                        snapshot.captured_at.isoformat(),
                        snapshot.portfolio_revision,
                        snapshot.projection_digest,
                        snapshot.model_dump_json(),
                    ),
                )
            except sqlite3.IntegrityError as exc:
                raise PortfolioAccountingError(
                    "portfolio analytics snapshot identity already exists"
                ) from exc

    def list(self, portfolio_id: UUID) -> tuple[PortfolioAnalyticsSnapshot, ...]:
        self.initialize()
        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT payload_json
                FROM portfolio_analytics_snapshots
                WHERE portfolio_id = ?
                ORDER BY captured_at, snapshot_id
                """,
                (str(portfolio_id),),
            ).fetchall()
        return tuple(
            PortfolioAnalyticsSnapshot.model_validate_json(str(row[0])) for row in rows
        )


class PortfolioAnalyticsService:
    """Build performance, attribution, scenario, and benchmark research evidence."""

    def __init__(self, accounting: PortfolioAccountingService) -> None:
        self.accounting = accounting
        self.store = PortfolioAnalyticsStore(str(accounting.store.database_path))

    def capture_snapshot(
        self,
        portfolio_id: UUID,
        *,
        captured_at: datetime | None = None,
    ) -> PortfolioAnalyticsSnapshot:
        projection = self.accounting.project(portfolio_id)
        if projection.health is not ProjectionHealth.HEALTHY:
            raise PortfolioAccountingError(
                "analytics snapshot requires complete valuation evidence"
            )
        if projection.equity_base is None:
            raise PortfolioAccountingError("analytics snapshot requires portfolio equity")
        valuations = self.accounting.valuations(portfolio_id)
        payload = projection.model_dump(mode="json")
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        timestamp = captured_at or datetime.now(UTC)
        snapshot = PortfolioAnalyticsSnapshot(
            portfolio_id=portfolio_id,
            captured_at=timestamp,
            portfolio_revision=projection.revision,
            projection_digest=digest,
            valuation_ids=tuple(item.observation_id for item in valuations),
            projection=projection,
        )
        self.store.append(snapshot)
        return snapshot

    def list_snapshots(
        self,
        portfolio_id: UUID,
    ) -> tuple[PortfolioAnalyticsSnapshot, ...]:
        self.accounting.get_portfolio(portfolio_id)
        return self.store.list(portfolio_id)

    def performance_report(self, portfolio_id: UUID) -> PortfolioPerformanceReport:
        portfolio = self.accounting.get_portfolio(portfolio_id)
        snapshots = self.list_snapshots(portfolio_id)
        if not snapshots:
            raise PortfolioAccountingError(
                "capture at least one complete analytics snapshot first"
            )
        equities = tuple(_snapshot_equity(item) for item in snapshots)
        initial_equity = equities[0]
        if initial_equity <= ZERO:
            raise PortfolioAccountingError("initial analytics equity must be positive")
        peak = equities[0]
        points: list[PortfolioPerformancePoint] = []
        max_drawdown = ZERO
        for snapshot, equity in zip(snapshots, equities, strict=True):
            if equity > peak:
                peak = equity
            drawdown = equity / peak - ONE if peak > ZERO else ZERO
            if drawdown < max_drawdown:
                max_drawdown = drawdown
            points.append(
                PortfolioPerformancePoint(
                    snapshot_id=snapshot.snapshot_id,
                    captured_at=snapshot.captured_at,
                    equity_base=equity,
                    cumulative_return=equity / initial_equity - ONE,
                    drawdown=drawdown,
                )
            )
        return PortfolioPerformanceReport(
            portfolio_id=portfolio_id,
            base_currency=portfolio.base_currency,
            evidence_start=snapshots[0].captured_at,
            evidence_end=snapshots[-1].captured_at,
            snapshot_count=len(snapshots),
            cumulative_return=equities[-1] / initial_equity - ONE,
            max_drawdown=max_drawdown,
            points=tuple(points),
        )

    def attribution_report(self, portfolio_id: UUID) -> PortfolioAttributionReport:
        portfolio = self.accounting.get_portfolio(portfolio_id)
        projection = self.accounting.project(portfolio_id)
        latest = _latest_valuations(self.accounting.valuations(portfolio_id))
        missing = list(projection.missing_evidence)
        values: list[tuple[PortfolioAttributionItem, Decimal]] = []
        total_market = ZERO
        for position in projection.positions:
            observation = latest.get(position.instrument_id)
            if observation is None:
                missing.append(f"missing price evidence for {position.instrument_id}")
                continue
            if observation.price_currency != position.currency:
                missing.append(
                    f"valuation currency mismatch for {position.instrument_id}: "
                    f"{observation.price_currency} vs {position.currency}"
                )
                continue
            rate = _base_rate(portfolio.base_currency, observation)
            if rate is None:
                missing.append(
                    f"missing FX evidence for {position.instrument_id} "
                    f"{position.currency}->{portfolio.base_currency}"
                )
                continue
            market_value = position.quantity * observation.unit_price * rate
            book_cost = position.book_cost * rate
            total_market += abs(market_value)
            values.append(
                (
                    PortfolioAttributionItem(
                        instrument_id=position.instrument_id,
                        market_value_base=market_value,
                        book_cost_base=book_cost,
                        unrealized_pnl_base=market_value - book_cost,
                        allocation=ZERO,
                        price_source=observation.price_source,
                        price_effective_at=observation.price_effective_at,
                        fx_source=observation.fx_source,
                        fx_effective_at=observation.fx_effective_at,
                    ),
                    market_value,
                )
            )
        items = tuple(
            item.model_copy(
                update={
                    "allocation": (
                        abs(market_value) / total_market if total_market > ZERO else ZERO
                    )
                }
            )
            for item, market_value in values
        )
        health = ProjectionHealth.HEALTHY if not missing else ProjectionHealth.DEGRADED
        return PortfolioAttributionReport(
            portfolio_id=portfolio_id,
            base_currency=portfolio.base_currency,
            health=health,
            missing_evidence=tuple(sorted(set(missing))),
            items=items,
        )

    def scenario_report(
        self,
        portfolio_id: UUID,
        *,
        asset_shocks: dict[str, Decimal],
        fx_shocks: dict[str, Decimal] | None = None,
    ) -> PortfolioScenarioReport:
        portfolio = self.accounting.get_portfolio(portfolio_id)
        projection = self.accounting.project(portfolio_id)
        if projection.health is not ProjectionHealth.HEALTHY:
            raise PortfolioAccountingError(
                "scenario analysis requires complete baseline valuation evidence"
            )
        if projection.equity_base is None:
            raise PortfolioAccountingError("scenario analysis requires baseline equity")
        normalized_asset_shocks = _validate_shocks(asset_shocks, "asset")
        normalized_fx_shocks = _validate_shocks(fx_shocks or {}, "FX")
        if portfolio.base_currency in normalized_fx_shocks:
            raise PortfolioAccountingError("base currency cannot receive an FX shock")
        latest = _latest_valuations(self.accounting.valuations(portfolio_id))
        cash_base = ZERO
        for currency, amount in projection.cash_by_currency.items():
            if currency == portfolio.base_currency:
                cash_base += amount
                continue
            currency_observation = latest.get(f"currency:{currency}")
            if currency_observation is None or currency_observation.fx_rate_to_base is None:
                raise PortfolioAccountingError(
                    f"scenario analysis is missing FX evidence for cash currency {currency}"
                )
            fx_multiplier = ONE + normalized_fx_shocks.get(currency, ZERO)
            cash_base += amount * currency_observation.fx_rate_to_base * fx_multiplier

        market_total = ZERO
        book_total = ZERO
        gross_exposure = ZERO
        for position in projection.positions:
            observation = latest.get(position.instrument_id)
            if observation is None:
                raise PortfolioAccountingError(
                    f"scenario analysis is missing price evidence for {position.instrument_id}"
                )
            if observation.price_currency != position.currency:
                raise PortfolioAccountingError(
                    f"scenario valuation currency mismatch for {position.instrument_id}"
                )
            base_rate = _base_rate(portfolio.base_currency, observation)
            if base_rate is None:
                raise PortfolioAccountingError(
                    f"scenario analysis is missing FX evidence for {position.instrument_id}"
                )
            price_multiplier = ONE + normalized_asset_shocks.get(
                position.instrument_id,
                ZERO,
            )
            fx_multiplier = ONE + normalized_fx_shocks.get(position.currency, ZERO)
            shocked_rate = base_rate * fx_multiplier
            market_value = (
                position.quantity
                * observation.unit_price
                * price_multiplier
                * shocked_rate
            )
            book_value = position.book_cost * shocked_rate
            market_total += market_value
            book_total += book_value
            gross_exposure += abs(market_value)
        scenario_equity = cash_base + market_total
        return PortfolioScenarioReport(
            portfolio_id=portfolio_id,
            base_currency=portfolio.base_currency,
            baseline_equity=projection.equity_base,
            scenario_equity=scenario_equity,
            equity_change=scenario_equity - projection.equity_base,
            shocked_unrealized_pnl=market_total - book_total,
            gross_exposure=gross_exposure,
            asset_shocks=normalized_asset_shocks,
            fx_shocks=normalized_fx_shocks,
        )

    def benchmark_comparison(
        self,
        portfolio_id: UUID,
        benchmark: tuple[BenchmarkObservation, ...],
    ) -> PortfolioBenchmarkComparison:
        report = self.performance_report(portfolio_id)
        if len(benchmark) < 2:
            raise PortfolioAccountingError("benchmark comparison requires at least two points")
        ordered = tuple(sorted(benchmark, key=lambda item: item.observed_at))
        if ordered[0].observed_at > report.evidence_start:
            raise PortfolioAccountingError(
                "benchmark evidence must begin no later than portfolio evidence"
            )
        if ordered[-1].observed_at < report.evidence_end:
            raise PortfolioAccountingError(
                "benchmark evidence must end no earlier than portfolio evidence"
            )
        first = ordered[0].value
        last = ordered[-1].value
        benchmark_return = last / first - ONE
        return PortfolioBenchmarkComparison(
            portfolio_id=portfolio_id,
            evidence_start=report.evidence_start,
            evidence_end=report.evidence_end,
            portfolio_return=report.cumulative_return,
            benchmark_return=benchmark_return,
            excess_return=report.cumulative_return - benchmark_return,
            benchmark_source_ids=tuple(
                dict.fromkeys(item.source_id for item in ordered)
            ),
        )


def _snapshot_equity(snapshot: PortfolioAnalyticsSnapshot) -> Decimal:
    equity = snapshot.projection.equity_base
    if equity is None:
        raise PortfolioAccountingError("retained analytics snapshot has no equity")
    return equity


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


def _base_rate(
    base_currency: str,
    observation: ValuationObservation,
) -> Decimal | None:
    if observation.price_currency == base_currency:
        return ONE
    return observation.fx_rate_to_base


def _validate_shocks(
    shocks: dict[str, Decimal],
    label: str,
) -> dict[str, Decimal]:
    normalized: dict[str, Decimal] = {}
    for key, shock in shocks.items():
        normalized_key = key.strip()
        if not normalized_key:
            raise PortfolioAccountingError(f"{label} shock identity cannot be blank")
        if not shock.is_finite() or shock <= Decimal("-1"):
            raise PortfolioAccountingError(
                f"{label} shock for {normalized_key} must be finite and greater than -1"
            )
        normalized[normalized_key] = shock
    return dict(sorted(normalized.items()))
