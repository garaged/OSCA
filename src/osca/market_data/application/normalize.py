from uuid import UUID

from osca.market_data.api import CanonicalDailyBar
from osca.provider.api import ProviderDailyObservation


class IncompleteObservationError(ValueError):
    pass


def normalize_daily(
    observation: ProviderDailyObservation,
    *,
    instrument_id: UUID,
    provider_id: str,
    request_id: UUID,
    volume_unit: str,
    normalization_revision: str,
) -> CanonicalDailyBar:
    if not observation.complete:
        raise IncompleteObservationError("incomplete observations cannot become canonical bars")
    return CanonicalDailyBar(
        instrument_id=instrument_id,
        effective_date=observation.effective_date,
        source_timestamp=observation.source_timestamp,
        open=observation.open,
        high=observation.high,
        low=observation.low,
        close=observation.close,
        volume=observation.volume,
        currency=observation.currency,
        volume_unit=volume_unit,
        provider_id=provider_id,
        source_identity=observation.source_identity,
        request_id=request_id,
        normalization_revision=normalization_revision,
    )
