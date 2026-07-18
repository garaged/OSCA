from osca.provider.api import (
    DailyProviderRequest,
    ProviderCapability,
    ProviderDailyObservation,
    ProviderFailure,
    ProviderFailureCode,
    ProviderResult,
)


class SyntheticDailyProvider:
    """Deterministic, license-safe adapter used only for contract conformance."""

    def __init__(
        self,
        capability: ProviderCapability,
        observations: tuple[ProviderDailyObservation, ...],
    ) -> None:
        self._capability = capability
        self._observations = observations

    def capability(self) -> ProviderCapability:
        return self._capability

    def retrieve_daily(self, request: DailyProviderRequest) -> ProviderResult:
        if not self._capability.rights.retrieval:
            return self._failure(request, ProviderFailureCode.POLICY, "retrieval is policy-blocked")
        if not self._capability.healthy:
            return self._failure(request, ProviderFailureCode.TRANSPORT, "provider is unavailable")
        if request.start_date < self._capability.earliest_date:
            return self._failure(request, ProviderFailureCode.COMPATIBILITY, "range is unsupported")
        selected = tuple(
            item
            for item in self._observations
            if request.start_date <= item.effective_date < request.end_date_exclusive
        )
        if not selected:
            return self._failure(
                request, ProviderFailureCode.MAPPING, "fixture has no mapped observations"
            )
        return ProviderResult(
            request_id=request.request_id,
            provider_id=self._capability.provider_id,
            observations=selected,
        )

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
