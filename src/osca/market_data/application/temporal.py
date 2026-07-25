from collections.abc import Iterable, Sequence
from datetime import UTC, datetime, time, timedelta
from uuid import UUID, uuid4

from osca.market_data.api.temporal import (
    INTERVAL_SECONDS,
    CanonicalOhlcvBar,
    CompletedBarWindow,
    ExchangeSession,
    MarketDataInterval,
    ResampleLineage,
    SessionState,
    TemporalGap,
    TemporalGapState,
)


def floor_to_interval(moment: datetime, interval: MarketDataInterval) -> datetime:
    if moment.tzinfo is None or moment.utcoffset() != UTC.utcoffset(moment):
        raise ValueError("moment must be expressed in UTC")
    seconds = INTERVAL_SECONDS[interval]
    epoch_seconds = int(moment.timestamp())
    floored = epoch_seconds - (epoch_seconds % seconds)
    return datetime.fromtimestamp(floored, tz=UTC)


def completed_bar_window(
    *,
    moment: datetime,
    interval: MarketDataInterval,
    publication_lag: timedelta = timedelta(),
) -> CompletedBarWindow:
    cutoff = moment - publication_lag
    end = floor_to_interval(cutoff, interval)
    return CompletedBarWindow(
        interval=interval,
        starts_at=end - timedelta(seconds=INTERVAL_SECONDS[interval]),
        ends_at=end,
    )


def stock_expected_windows(
    *,
    session: ExchangeSession,
    interval: MarketDataInterval,
) -> tuple[CompletedBarWindow, ...]:
    if session.state in {SessionState.CLOSED, SessionState.HOLIDAY}:
        return ()
    step = timedelta(seconds=INTERVAL_SECONDS[interval])
    if interval is MarketDataInterval.D1:
        day_start = datetime.combine(session.session_date, time.min, tzinfo=UTC)
        return (
            CompletedBarWindow(
                interval=interval,
                starts_at=day_start,
                ends_at=day_start + timedelta(days=1),
            ),
        )
    windows: list[CompletedBarWindow] = []
    cursor = session.opens_at
    while cursor + step <= session.closes_at:
        windows.append(
            CompletedBarWindow(interval=interval, starts_at=cursor, ends_at=cursor + step)
        )
        cursor += step
    return tuple(windows)


def crypto_expected_windows(
    *,
    day_start: datetime,
    interval: MarketDataInterval,
) -> tuple[CompletedBarWindow, ...]:
    if day_start.tzinfo is None or day_start.utcoffset() != UTC.utcoffset(day_start):
        raise ValueError("crypto day start must be expressed in UTC")
    step = timedelta(seconds=INTERVAL_SECONDS[interval])
    if interval is MarketDataInterval.D1:
        return (
            CompletedBarWindow(
                interval=interval,
                starts_at=day_start,
                ends_at=day_start + step,
            ),
        )
    day_end = day_start + timedelta(days=1)
    windows: list[CompletedBarWindow] = []
    cursor = day_start
    while cursor + step <= day_end:
        windows.append(CompletedBarWindow(interval=interval, starts_at=cursor, ends_at=cursor + step))
        cursor += step
    return tuple(windows)


def classify_temporal_gaps(
    *,
    instrument_id: UUID,
    interval: MarketDataInterval,
    expected_windows: Sequence[CompletedBarWindow] | None,
    observed_windows: frozenset[tuple[datetime, datetime]],
    current_completed_end: datetime,
    calendar_revision: str,
) -> tuple[TemporalGap, ...]:
    if expected_windows is None:
        return (
            TemporalGap(
                instrument_id=instrument_id,
                interval=interval,
                starts_at=current_completed_end,
                ends_at=current_completed_end,
                state=TemporalGapState.UNRESOLVED,
                reason="calendar_session_unresolved",
                repair_eligible=False,
                calendar_revision=calendar_revision,
            ),
        )
    gaps: list[TemporalGap] = []
    for window in expected_windows:
        if window.ends_at > current_completed_end:
            state, reason, repair_eligible = (
                TemporalGapState.INCOMPLETE,
                "bar_not_complete",
                False,
            )
        elif (window.starts_at, window.ends_at) in observed_windows:
            state, reason, repair_eligible = (
                TemporalGapState.OBSERVED,
                "complete_observation",
                False,
            )
        else:
            state, reason, repair_eligible = (
                TemporalGapState.MISSING,
                "expected_completed_bar_missing",
                True,
            )
        gaps.append(
            TemporalGap(
                instrument_id=instrument_id,
                interval=interval,
                starts_at=window.starts_at,
                ends_at=window.ends_at,
                state=state,
                reason=reason,
                repair_eligible=repair_eligible,
                calendar_revision=calendar_revision,
            )
        )
    return tuple(gaps)


def resample_ohlcv(
    bars: Sequence[CanonicalOhlcvBar],
    *,
    target_interval: MarketDataInterval,
    request_id: UUID | None = None,
) -> tuple[tuple[CanonicalOhlcvBar, ResampleLineage], ...]:
    if not bars:
        return ()
    ordered = tuple(sorted(bars, key=lambda bar: bar.starts_at))
    source_interval = ordered[0].interval
    if any(bar.interval is not source_interval for bar in ordered):
        raise ValueError("resampling requires a single source interval")
    if INTERVAL_SECONDS[source_interval] >= INTERVAL_SECONDS[target_interval]:
        raise ValueError("resampling requires a lower source interval")
    grouped: dict[datetime, list[CanonicalOhlcvBar]] = {}
    for bar in ordered:
        target_start = floor_to_interval(bar.starts_at, target_interval)
        grouped.setdefault(target_start, []).append(bar)
    results: list[tuple[CanonicalOhlcvBar, ResampleLineage]] = []
    target_seconds = INTERVAL_SECONDS[target_interval]
    source_seconds = INTERVAL_SECONDS[source_interval]
    expected_count = target_seconds // source_seconds
    for target_start, group in sorted(grouped.items()):
        if len(group) != expected_count:
            continue
        target_end = target_start + timedelta(seconds=target_seconds)
        if group[0].starts_at != target_start or group[-1].ends_at != target_end:
            continue
        if any(current.ends_at != nxt.starts_at for current, nxt in pairwise(group)):
            continue
        output = _combine_group(
            group,
            target_interval=target_interval,
            target_start=target_start,
            target_end=target_end,
            request_id=request_id or uuid4(),
        )
        lineage = ResampleLineage(
            output_bar_id=output.bar_id,
            source_bar_ids=tuple(bar.bar_id for bar in group),
            source_interval=source_interval,
            target_interval=target_interval,
            calendar_revision=output.calendar_revision,
        )
        results.append((output, lineage))
    return tuple(results)


def pairwise(
    items: Sequence[CanonicalOhlcvBar],
) -> Iterable[tuple[CanonicalOhlcvBar, CanonicalOhlcvBar]]:
    for index in range(len(items) - 1):
        yield items[index], items[index + 1]


def _combine_group(
    group: Sequence[CanonicalOhlcvBar],
    *,
    target_interval: MarketDataInterval,
    target_start: datetime,
    target_end: datetime,
    request_id: UUID,
) -> CanonicalOhlcvBar:
    first = group[0]
    if any(bar.instrument_id != first.instrument_id for bar in group):
        raise ValueError("resampling group cannot mix instruments")
    if any(
        bar.currency != first.currency or bar.volume_unit != first.volume_unit
        for bar in group
    ):
        raise ValueError("resampling group cannot mix units")
    if any(bar.provider_id != first.provider_id for bar in group):
        raise ValueError("resampling group cannot mix providers")
    calendar_revisions = {bar.calendar_revision for bar in group}
    if len(calendar_revisions) != 1:
        raise ValueError("resampling group cannot mix calendar revisions")
    return CanonicalOhlcvBar(
        instrument_id=first.instrument_id,
        interval=target_interval,
        starts_at=target_start,
        ends_at=target_end,
        effective_date=target_start.date(),
        open=first.open,
        high=max(bar.high for bar in group),
        low=min(bar.low for bar in group),
        close=group[-1].close,
        volume=sum((bar.volume for bar in group), start=first.volume * 0),
        currency=first.currency,
        volume_unit=first.volume_unit,
        provider_id=first.provider_id,
        source_identity="resampled:" + ",".join(str(bar.bar_id) for bar in group),
        request_id=request_id,
        normalization_revision="ohlcv-resample-v1",
        calendar_revision=first.calendar_revision,
    )
