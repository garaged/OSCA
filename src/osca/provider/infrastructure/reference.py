from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from osca.provider.api import (
    DailyProviderRequest,
    ProviderCapability,
    ProviderDailyObservation,
    ProviderFailure,
    ProviderFailureCode,
    ProviderResult,
)

ProviderPayload = Mapping[str, Any]
ProviderFetch = Callable[[DailyProviderRequest], ProviderPayload]


class ReferenceDailyProvider:
    """Provider parser with injected I/O so credentials and HTTP remain at the edge."""

    def __init__(
        self,
        capability: ProviderCapability,
        fetch: ProviderFetch,
        quote_currency: str,
    ) -> None:
        self._capability = capability
        self._fetch = fetch
        self._quote_currency = quote_currency

    def capability(self) -> ProviderCapability:
        return self._capability

    def retrieve_daily(self, request: DailyProviderRequest) -> ProviderResult:
        if not self._capability.rights.retrieval:
            return self._failure(request, ProviderFailureCode.POLICY, "retrieval is policy-blocked")
        try:
            payload = self._fetch(request)
            observations = self._parse(request, payload)
        except (InvalidOperation, KeyError, TypeError, ValueError):
            return self._failure(
                request,
                ProviderFailureCode.SCHEMA,
                "provider response did not match the governed daily schema",
            )
        if not observations:
            return self._failure(
                request,
                ProviderFailureCode.MAPPING,
                "provider returned no completed observations for the requested mapping",
            )
        return ProviderResult(
            request_id=request.request_id,
            provider_id=self._capability.provider_id,
            observations=observations,
        )

    def _parse(
        self, request: DailyProviderRequest, payload: ProviderPayload
    ) -> tuple[ProviderDailyObservation, ...]:
        raise NotImplementedError

    def _failure(
        self,
        request: DailyProviderRequest,
        code: ProviderFailureCode,
        message: str,
    ) -> ProviderResult:
        return ProviderResult(
            request_id=request.request_id,
            provider_id=self._capability.provider_id,
            failure=ProviderFailure(code=code, retryable=False, safe_message=message),
        )

    def _observation(
        self,
        request: DailyProviderRequest,
        *,
        effective_date: datetime,
        source_timestamp: datetime,
        row: Mapping[str, Any],
    ) -> ProviderDailyObservation | None:
        day = effective_date.date()
        if not (request.start_date <= day < request.end_date_exclusive):
            return None
        if day > self._capability.latest_completed_date:
            return None
        return ProviderDailyObservation(
            effective_date=day,
            source_timestamp=source_timestamp,
            complete=True,
            open=Decimal(str(row["open"])),
            high=Decimal(str(row["high"])),
            low=Decimal(str(row["low"])),
            close=Decimal(str(row["close"])),
            volume=Decimal(str(row["volume"])),
            currency=self._quote_currency,
            source_identity=(
                f"{self._capability.provider_id}:{request.provider_symbol}:{day.isoformat()}"
            ),
        )


class TwelveDataDailyProvider(ReferenceDailyProvider):
    def _parse(
        self, request: DailyProviderRequest, payload: ProviderPayload
    ) -> tuple[ProviderDailyObservation, ...]:
        if payload.get("status") == "error":
            raise ValueError("provider error envelope")
        values = payload["values"]
        if not isinstance(values, list):
            raise TypeError("values must be a list")
        observations: list[ProviderDailyObservation] = []
        for value in values:
            if not isinstance(value, Mapping):
                raise TypeError("daily value must be an object")
            timestamp = datetime.fromisoformat(str(value["datetime"])).replace(tzinfo=UTC)
            observation = self._observation(
                request,
                effective_date=timestamp,
                source_timestamp=timestamp,
                row=value,
            )
            if observation is not None:
                observations.append(observation)
        return tuple(sorted(observations, key=lambda item: item.effective_date))


class KrakenDailyProvider(ReferenceDailyProvider):
    def _parse(
        self, request: DailyProviderRequest, payload: ProviderPayload
    ) -> tuple[ProviderDailyObservation, ...]:
        errors = payload["error"]
        if not isinstance(errors, list) or errors:
            raise ValueError("provider error envelope")
        result = payload["result"]
        if not isinstance(result, Mapping):
            raise TypeError("result must be an object")
        series_values = [value for key, value in result.items() if key != "last"]
        if len(series_values) != 1:
            raise ValueError("result must contain exactly one requested OHLC series")
        series = series_values[0]
        if not isinstance(series, list):
            raise TypeError("OHLC series must be a list")
        observations: list[ProviderDailyObservation] = []
        for value in series:
            if not isinstance(value, list) or len(value) < 7:
                raise TypeError("OHLC row must contain seven fields")
            interval_start = datetime.fromtimestamp(int(value[0]), tz=UTC)
            row = {
                "open": value[1],
                "high": value[2],
                "low": value[3],
                "close": value[4],
                "volume": value[6],
            }
            observation = self._observation(
                request,
                effective_date=interval_start,
                source_timestamp=interval_start + timedelta(days=1),
                row=row,
            )
            if observation is not None:
                observations.append(observation)
        return tuple(sorted(observations, key=lambda item: item.effective_date))
