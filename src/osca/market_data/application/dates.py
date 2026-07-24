from datetime import date, timedelta
from uuid import UUID

from osca.instrument.api import AssetClass
from osca.market_data.api import DateClassification, DateFinding


def classify_dates(
    *,
    instrument_id: UUID,
    asset_class: AssetClass,
    start_date: date,
    end_date_exclusive: date,
    current_utc_date: date,
    observed: frozenset[date],
    confirmed_stock_sessions: frozenset[date] = frozenset(),
) -> tuple[DateFinding, ...]:
    if start_date >= end_date_exclusive:
        raise ValueError("date range must be non-empty")
    findings: list[DateFinding] = []
    candidate = start_date
    while candidate < end_date_exclusive:
        classification, reason, repair_eligible = _classify(
            asset_class=asset_class,
            candidate=candidate,
            current_utc_date=current_utc_date,
            observed=observed,
            confirmed_stock_sessions=confirmed_stock_sessions,
        )
        findings.append(
            DateFinding(
                instrument_id=instrument_id,
                effective_date=candidate,
                classification=classification,
                reason=reason,
                repair_eligible=repair_eligible,
            )
        )
        candidate += timedelta(days=1)
    return tuple(findings)


def contiguous_missing_ranges(
    findings: tuple[DateFinding, ...],
) -> tuple[tuple[date, date], ...]:
    missing = sorted(
        finding.effective_date
        for finding in findings
        if finding.classification is DateClassification.MISSING and finding.repair_eligible
    )
    if not missing:
        return ()
    ranges: list[tuple[date, date]] = []
    start = previous = missing[0]
    for candidate in missing[1:]:
        if candidate != previous + timedelta(days=1):
            ranges.append((start, previous + timedelta(days=1)))
            start = candidate
        previous = candidate
    ranges.append((start, previous + timedelta(days=1)))
    return tuple(ranges)


def _classify(
    *,
    asset_class: AssetClass,
    candidate: date,
    current_utc_date: date,
    observed: frozenset[date],
    confirmed_stock_sessions: frozenset[date],
) -> tuple[DateClassification, str, bool]:
    if candidate >= current_utc_date:
        return DateClassification.INCOMPLETE, "utc_interval_incomplete", False
    if candidate in observed:
        return DateClassification.OBSERVED, "complete_observation", False
    if asset_class is AssetClass.CRYPTO_PAIR:
        return DateClassification.MISSING, "completed_utc_date_missing", True
    if candidate.weekday() >= 5:
        return DateClassification.NON_EXPECTED, "stock_weekend", False
    if candidate in confirmed_stock_sessions:
        return DateClassification.MISSING, "confirmed_stock_session_missing", True
    return DateClassification.UNRESOLVED, "stock_session_uncertain", False
