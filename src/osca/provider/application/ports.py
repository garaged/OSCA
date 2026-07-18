from typing import Protocol

from osca.provider.api import DailyProviderRequest, ProviderCapability, ProviderResult


class DailyProviderAdapter(Protocol):
    def capability(self) -> ProviderCapability: ...
    def retrieve_daily(self, request: DailyProviderRequest) -> ProviderResult: ...
