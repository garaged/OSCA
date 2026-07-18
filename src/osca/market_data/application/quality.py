from datetime import date
from uuid import UUID

from osca.market_data.api import CanonicalDailyBar, DateClassification, DateFinding


def validate_daily_series(
    bars: tuple[CanonicalDailyBar, ...],
    *,
    instrument_id: UUID,
    start_date: date,
    end_date_exclusive: date,
) -> tuple[DateFinding, ...]:
    """Return deterministic set-level findings without mutating observations."""
    if start_date >= end_date_exclusive:
        raise ValueError("date range must be non-empty")
    findings: list[DateFinding] = []
    counts: dict[date, int] = {}
    for bar in bars:
        counts[bar.effective_date] = counts.get(bar.effective_date, 0) + 1
        if bar.instrument_id != instrument_id:
            findings.append(
                DateFinding(
                    instrument_id=instrument_id,
                    effective_date=bar.effective_date,
                    classification=DateClassification.INVALID,
                    reason="canonical_instrument_mismatch",
                    repair_eligible=False,
                )
            )
        if not start_date <= bar.effective_date < end_date_exclusive:
            findings.append(
                DateFinding(
                    instrument_id=instrument_id,
                    effective_date=bar.effective_date,
                    classification=DateClassification.INVALID,
                    reason="observation_outside_declared_range",
                    repair_eligible=False,
                )
            )
    findings.extend(
        DateFinding(
            instrument_id=instrument_id,
            effective_date=effective_date,
            classification=DateClassification.DUPLICATE,
            reason="duplicate_canonical_instrument_date",
            repair_eligible=False,
        )
        for effective_date, count in counts.items()
        if count > 1
    )
    return tuple(
        sorted(
            findings,
            key=lambda finding: (
                finding.effective_date,
                finding.classification,
                finding.reason,
            ),
        )
    )
