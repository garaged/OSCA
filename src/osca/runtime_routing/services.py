from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Literal
from urllib.parse import unquote, urlparse

from pydantic import ValidationError

from osca.provider_adapters import ProviderAdapterEndpoint
from osca.provider_catalog import ProviderCatalogIdentifier
from osca.provider_preview import (
    FredPreviewRequest,
    ProviderPreviewError,
    ProviderPreviewMode,
    SecPreviewRequest,
    SecPreviewService,
    evaluate_fred_preview,
)
from osca.runtime_routing.contracts import (
    RuntimeRoutingBatchOutcome,
    RuntimeRoutingBatchResult,
    RuntimeRoutingCapability,
    RuntimeRoutingDecision,
    RuntimeRoutingRequest,
    RuntimeRoutingSource,
    RuntimeRoutingStatus,
)

_LOCAL_PROVIDER_ALIASES = {"local", "local_ohlcv", "local-file"}
_SEC_PROVIDER_ALIASES = {"sec", "sec_edgar", "sec-edgar"}
_FRED_PROVIDER_ALIASES = {"fred"}


class RuntimeRouter:
    def __init__(self, *, sec_preview_service: SecPreviewService | None = None) -> None:
        self._sec_preview_service = sec_preview_service or SecPreviewService()

    def route(
        self,
        request: RuntimeRoutingRequest,
        *,
        storage_root: Path,
    ) -> RuntimeRoutingDecision:
        if request.capability is RuntimeRoutingCapability.OHLCV:
            return self._route_local_ohlcv(request)
        if request.capability in {
            RuntimeRoutingCapability.COMPANY_FACTS,
            RuntimeRoutingCapability.FILINGS,
        }:
            return self._route_sec(request, storage_root=storage_root)
        return self._route_macro(request)

    def route_many(
        self,
        requests: Iterable[RuntimeRoutingRequest],
        *,
        storage_root: Path,
    ) -> RuntimeRoutingBatchResult:
        decisions = tuple(
            self.route(request, storage_root=storage_root) for request in requests
        )
        if not decisions:
            raise ValueError("runtime routing batch must contain at least one request")
        selected_count = sum(
            decision.status is RuntimeRoutingStatus.SELECTED for decision in decisions
        )
        blocked_count = sum(
            decision.status is RuntimeRoutingStatus.POLICY_BLOCKED
            for decision in decisions
        )
        unavailable_count = sum(
            decision.status is RuntimeRoutingStatus.PROVIDER_UNAVAILABLE
            for decision in decisions
        )
        if selected_count == len(decisions):
            outcome = RuntimeRoutingBatchOutcome.SUCCEEDED
        elif selected_count > 0:
            outcome = RuntimeRoutingBatchOutcome.PARTIAL
        elif blocked_count > 0:
            outcome = RuntimeRoutingBatchOutcome.BLOCKED
        else:
            outcome = RuntimeRoutingBatchOutcome.UNAVAILABLE
        non_macro_continued = any(
            decision.capability is RuntimeRoutingCapability.MACRO_SERIES
            and decision.status is not RuntimeRoutingStatus.SELECTED
            for decision in decisions
        ) and any(
            decision.capability is not RuntimeRoutingCapability.MACRO_SERIES
            and decision.status is RuntimeRoutingStatus.SELECTED
            for decision in decisions
        )
        return RuntimeRoutingBatchResult(
            outcome=outcome,
            decisions=decisions,
            selected_count=selected_count,
            policy_blocked_count=blocked_count,
            provider_unavailable_count=unavailable_count,
            non_macro_continued=non_macro_continued,
        )

    def _route_local_ohlcv(
        self,
        request: RuntimeRoutingRequest,
    ) -> RuntimeRoutingDecision:
        provider = _normalized_provider(request.preferred_provider)
        if provider is not None and provider not in _LOCAL_PROVIDER_ALIASES:
            return _unavailable(
                request,
                rationale="Requested OHLCV provider is not enabled for runtime routing.",
                finding_ids=("ohlcv-provider-not-enabled",),
            )
        if request.local_payload_uri is None:
            return _unavailable(
                request,
                rationale="No governed local OHLCV payload was supplied.",
                finding_ids=("local-ohlcv-payload-not-supplied",),
            )
        payload_path = _local_path(request.local_payload_uri)
        if not payload_path.is_file():
            return _unavailable(
                request,
                rationale="The governed local OHLCV payload is unavailable.",
                finding_ids=("local-ohlcv-payload-unavailable",),
            )
        if payload_path.suffix.lower() not in {".parquet", ".pq"}:
            return _unavailable(
                request,
                rationale="Runtime OHLCV routing requires a governed Parquet payload.",
                finding_ids=("local-ohlcv-payload-format-unsupported",),
            )
        stale = _is_stale(
            payload_path,
            requested_at=request.requested_at,
            max_age_seconds=request.max_age_seconds,
        )
        if stale and not request.allow_stale:
            return _unavailable(
                request,
                rationale=(
                    "The only governed local OHLCV payload is stale and stale use "
                    "was not allowed."
                ),
                finding_ids=("local-ohlcv-payload-stale",),
            )
        findings = ("selected-source-stale",) if stale else ()
        payload_uri = payload_path.resolve().as_uri()
        return RuntimeRoutingDecision(
            request_id=request.request_id,
            capability=request.capability,
            resource_id=request.resource_id,
            status=RuntimeRoutingStatus.SELECTED,
            selected_source=RuntimeRoutingSource.LOCAL_OHLCV,
            source_uri=payload_uri,
            payload_uri=payload_uri,
            stale=stale,
            network_access_enabled=False,
            rationale=(
                "Selected the explicitly supplied governed local OHLCV payload."
                if not stale
                else (
                    "Selected the explicitly supplied stale local OHLCV payload "
                    "because stale use was allowed."
                )
            ),
            finding_ids=findings,
        )

    def _route_sec(
        self,
        request: RuntimeRoutingRequest,
        *,
        storage_root: Path,
    ) -> RuntimeRoutingDecision:
        provider = _normalized_provider(request.preferred_provider)
        if provider is not None and provider not in _SEC_PROVIDER_ALIASES:
            return _unavailable(
                request,
                rationale=(
                    "Requested enrichment provider is not enabled for this capability."
                ),
                finding_ids=("enrichment-provider-not-enabled",),
            )
        if request.fixture_path is None and not request.network_access_enabled:
            return _unavailable(
                request,
                rationale=(
                    "SEC routing requires an explicit fixture or opt-in live preview."
                ),
                finding_ids=("sec-source-not-supplied",),
                provider_id=ProviderCatalogIdentifier.SEC_EDGAR,
            )
        endpoint: Literal[
            ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
            ProviderAdapterEndpoint.SEC_SUBMISSIONS,
        ] = (
            ProviderAdapterEndpoint.SEC_COMPANY_FACTS
            if request.capability is RuntimeRoutingCapability.COMPANY_FACTS
            else ProviderAdapterEndpoint.SEC_SUBMISSIONS
        )
        try:
            preview_request = SecPreviewRequest(
                endpoint=endpoint,
                cik=request.resource_id,
                network_access_enabled=request.network_access_enabled,
                fixture_path=request.fixture_path,
                user_agent=request.user_agent,
                force_refresh=request.force_refresh,
            )
            evidence = self._sec_preview_service.run(
                preview_request,
                storage_root=storage_root,
            )
        except (ProviderPreviewError, ValidationError, OSError, ValueError) as exc:
            return _unavailable(
                request,
                rationale=f"SEC source could not satisfy the routing request: {exc}",
                finding_ids=("sec-source-unavailable",),
                provider_id=ProviderCatalogIdentifier.SEC_EDGAR,
            )
        if evidence.payload_uri is None:
            return _unavailable(
                request,
                rationale="SEC preview completed without selectable payload evidence.",
                finding_ids=("sec-payload-unavailable",),
                provider_id=ProviderCatalogIdentifier.SEC_EDGAR,
            )
        payload_path = _local_path(evidence.payload_uri)
        stale = _is_stale(
            payload_path,
            requested_at=request.requested_at,
            max_age_seconds=request.max_age_seconds,
        )
        if stale and not request.allow_stale:
            return _unavailable(
                request,
                rationale=(
                    "The available SEC payload is stale and stale use was not allowed."
                ),
                finding_ids=(*evidence.finding_ids, "sec-payload-stale"),
                provider_id=ProviderCatalogIdentifier.SEC_EDGAR,
            )
        source = (
            RuntimeRoutingSource.SEC_EDGAR_FIXTURE
            if evidence.mode is ProviderPreviewMode.FIXTURE_REPLAY
            else RuntimeRoutingSource.SEC_EDGAR_LIVE_PREVIEW
        )
        findings = (
            (*evidence.finding_ids, "selected-source-stale")
            if stale
            else evidence.finding_ids
        )
        return RuntimeRoutingDecision(
            request_id=request.request_id,
            capability=request.capability,
            resource_id=request.resource_id,
            status=RuntimeRoutingStatus.SELECTED,
            selected_source=source,
            provider_id=ProviderCatalogIdentifier.SEC_EDGAR,
            source_uri=evidence.source_uri,
            payload_uri=evidence.payload_uri,
            metadata_uri=evidence.metadata_uri,
            stale=stale,
            cache_hit=evidence.cache_hit,
            network_access_used=evidence.network_access_used,
            network_access_enabled=evidence.network_access_enabled,
            rationale=(
                "Selected SEC EDGAR fixture evidence through governed runtime routing."
                if source is RuntimeRoutingSource.SEC_EDGAR_FIXTURE
                else (
                    "Selected explicit opt-in SEC EDGAR live-preview evidence through "
                    "governed runtime routing."
                )
            ),
            finding_ids=findings,
        )

    def _route_macro(
        self,
        request: RuntimeRoutingRequest,
    ) -> RuntimeRoutingDecision:
        provider = _normalized_provider(request.preferred_provider) or "fred"
        if provider not in _FRED_PROVIDER_ALIASES:
            return _unavailable(
                request,
                rationale="No approved runtime macro-series provider is available.",
                finding_ids=("macro-provider-unavailable",),
            )
        try:
            evidence = evaluate_fred_preview(
                FredPreviewRequest(
                    series_id=request.resource_id,
                    network_access_enabled=request.network_access_enabled,
                    secret_reference=request.secret_reference,
                )
            )
            findings = evidence.finding_ids
            rationale = evidence.rationale
        except ValidationError:
            findings = (
                "fred-live-preview-policy-blocked",
                "fred-secret-reference-invalid-and-not-resolved",
            )
            rationale = (
                "FRED remains policy-blocked and the supplied credential reference "
                "was not resolved."
            )
        return RuntimeRoutingDecision(
            request_id=request.request_id,
            capability=request.capability,
            resource_id=request.resource_id,
            status=RuntimeRoutingStatus.POLICY_BLOCKED,
            provider_id=ProviderCatalogIdentifier.FRED,
            network_access_enabled=request.network_access_enabled,
            rationale=rationale,
            finding_ids=findings,
        )


def routing_policy() -> tuple[dict[str, object], ...]:
    return (
        {
            "capability": RuntimeRoutingCapability.OHLCV.value,
            "source_precedence": (RuntimeRoutingSource.LOCAL_OHLCV.value,),
            "missing_source_status": RuntimeRoutingStatus.PROVIDER_UNAVAILABLE.value,
        },
        {
            "capability": RuntimeRoutingCapability.COMPANY_FACTS.value,
            "source_precedence": (
                RuntimeRoutingSource.SEC_EDGAR_FIXTURE.value,
                RuntimeRoutingSource.SEC_EDGAR_LIVE_PREVIEW.value,
            ),
            "missing_source_status": RuntimeRoutingStatus.PROVIDER_UNAVAILABLE.value,
        },
        {
            "capability": RuntimeRoutingCapability.FILINGS.value,
            "source_precedence": (
                RuntimeRoutingSource.SEC_EDGAR_FIXTURE.value,
                RuntimeRoutingSource.SEC_EDGAR_LIVE_PREVIEW.value,
            ),
            "missing_source_status": RuntimeRoutingStatus.PROVIDER_UNAVAILABLE.value,
        },
        {
            "capability": RuntimeRoutingCapability.MACRO_SERIES.value,
            "source_precedence": (),
            "missing_source_status": RuntimeRoutingStatus.POLICY_BLOCKED.value,
            "note": (
                "FRED is optional and policy-blocked; non-macro routing continues "
                "independently."
            ),
        },
    )


def _normalized_provider(provider: str | None) -> str | None:
    return provider.strip().lower() if provider is not None else None


def _local_path(uri_or_path: str) -> Path:
    parsed = urlparse(uri_or_path)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path))
    if parsed.scheme:
        return Path("/__osca_non_local_uri__")
    return Path(uri_or_path)


def _is_stale(
    path: Path,
    *,
    requested_at: datetime,
    max_age_seconds: int | None,
) -> bool:
    if max_age_seconds is None:
        return False
    if not path.is_file():
        return True
    age_seconds = requested_at.timestamp() - path.stat().st_mtime
    return age_seconds > max_age_seconds


def _unavailable(
    request: RuntimeRoutingRequest,
    *,
    rationale: str,
    finding_ids: tuple[str, ...],
    provider_id: ProviderCatalogIdentifier | None = None,
) -> RuntimeRoutingDecision:
    return RuntimeRoutingDecision(
        request_id=request.request_id,
        capability=request.capability,
        resource_id=request.resource_id,
        status=RuntimeRoutingStatus.PROVIDER_UNAVAILABLE,
        provider_id=provider_id,
        network_access_enabled=request.network_access_enabled,
        rationale=rationale,
        finding_ids=finding_ids,
    )
