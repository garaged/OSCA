from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict

from osca.instrument.api import AssetClass
from osca.provider.api import (
    DailyProviderRequest,
    ProviderFailure,
    ProviderFailureCode,
    ProviderResult,
)
from osca.provider.application.ports import DailyProviderAdapter


class RoutedProviderResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.provider.routed-daily-result"] = (
        "osca.provider.routed-daily-result"
    )
    version: Literal["1.0.0"] = "1.0.0"
    result: ProviderResult
    attempted_provider_ids: tuple[str, ...]
    transitions: tuple[str, ...]


class DailyProviderRouter:
    def __init__(self, adapters: Mapping[str, DailyProviderAdapter]) -> None:
        self._adapters = dict(adapters)

    def retrieve(
        self,
        request: DailyProviderRequest,
        *,
        asset_class: AssetClass,
        ordered_provider_ids: tuple[str, ...],
    ) -> RoutedProviderResult:
        if not ordered_provider_ids:
            raise ValueError("routing requires an explicit ordered provider policy")
        attempts: list[str] = []
        transitions: list[str] = []
        last: ProviderResult | None = None
        for provider_id in ordered_provider_ids:
            adapter = self._adapters.get(provider_id)
            if adapter is None:
                continue
            capability = adapter.capability()
            if capability.provider_id != provider_id:
                raise ValueError("adapter identity differs from its routing key")
            if (
                asset_class not in capability.asset_classes
                or request.interval not in capability.intervals
                or request.start_date < capability.earliest_date
            ):
                continue
            attempts.append(provider_id)
            if not capability.rights.retrieval:
                last = _failure(request, provider_id, ProviderFailureCode.POLICY)
                break
            if not capability.healthy:
                last = _failure(request, provider_id, ProviderFailureCode.TRANSPORT)
            else:
                last = adapter.retrieve_daily(request)
            if last.failure is None:
                return RoutedProviderResult(
                    result=last,
                    attempted_provider_ids=tuple(attempts),
                    transitions=tuple(transitions),
                )
            if last.failure.code not in {
                ProviderFailureCode.QUOTA,
                ProviderFailureCode.TRANSPORT,
            }:
                break
            transitions.append(f"{provider_id}:{last.failure.code.value}")
        if last is None:
            last = _failure(request, "routing", ProviderFailureCode.COMPATIBILITY)
        return RoutedProviderResult(
            result=last,
            attempted_provider_ids=tuple(attempts),
            transitions=tuple(transitions),
        )


def _failure(
    request: DailyProviderRequest,
    provider_id: str,
    code: ProviderFailureCode,
) -> ProviderResult:
    messages = {
        ProviderFailureCode.POLICY: "provider retrieval is policy-blocked",
        ProviderFailureCode.TRANSPORT: "provider is unavailable",
        ProviderFailureCode.COMPATIBILITY: "no provider satisfies the requested capability",
    }
    return ProviderResult(
        request_id=request.request_id,
        provider_id=provider_id,
        failure=ProviderFailure(code=code, retryable=False, safe_message=messages[code]),
    )
