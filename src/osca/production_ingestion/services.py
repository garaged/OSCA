from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

from osca.production_ingestion.contracts import (
    AdmissionStatus,
    IngestionStatus,
    ProductionIngestionEvidence,
    ProductionIngestionRequest,
    ProductionProvider,
)
from osca.production_ingestion.policy import admission_for

Transport = Callable[[ProductionIngestionRequest], bytes]

_ALLOWED_HOSTS = {
    ProductionProvider.SEC_EDGAR: "data.sec.gov",
    ProductionProvider.KRAKEN: "api.kraken.com",
}
_ALLOWED_PATH_PREFIXES = {
    ProductionProvider.SEC_EDGAR: (
        "/api/xbrl/companyfacts/CIK",
        "/submissions/CIK",
    ),
    ProductionProvider.KRAKEN: ("/0/public/OHLC",),
}


def run_production_ingestion(
    request: ProductionIngestionRequest,
    *,
    transport: Transport | None = None,
) -> ProductionIngestionEvidence:
    admission = admission_for(request.provider_id)
    if admission.status is not AdmissionStatus.APPROVED:
        status = (
            IngestionStatus.POLICY_BLOCKED
            if admission.status is AdmissionStatus.POLICY_BLOCKED
            else IngestionStatus.PROVIDER_UNAVAILABLE
        )
        return _evidence(
            request,
            status=status,
            admission_status=admission.status,
            rationale=admission.rationale,
            findings=admission.findings,
        )
    if request.resource_id not in admission.approved_resources:
        return _evidence(
            request,
            status=IngestionStatus.POLICY_BLOCKED,
            admission_status=admission.status,
            rationale="Requested resource is outside the approved provider scope.",
            findings=("resource-not-admitted",),
        )
    endpoint_finding = _validate_endpoint(request)
    if endpoint_finding is not None:
        return _evidence(
            request,
            status=IngestionStatus.POLICY_BLOCKED,
            admission_status=admission.status,
            rationale="Endpoint is outside the approved production allowlist.",
            findings=(endpoint_finding,),
        )
    if not request.network_access_enabled:
        return _evidence(
            request,
            status=IngestionStatus.POLICY_BLOCKED,
            admission_status=admission.status,
            rationale="Production ingestion requires explicit network opt-in.",
            findings=("network-access-not-enabled",),
        )

    fetch = transport or _urllib_transport
    last_error = "provider-request-failed"
    for attempt in range(1, request.max_attempts + 1):
        try:
            payload = fetch(request)
            if len(payload) > request.max_response_bytes:
                return _evidence(
                    request,
                    status=IngestionStatus.FAILED,
                    admission_status=admission.status,
                    attempt_count=attempt,
                    network_used=True,
                    rationale="Provider response exceeded the configured size limit.",
                    findings=("response-size-limit-exceeded",),
                )
            json.loads(payload)
            return _retain_success(request, payload, attempt)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < request.max_attempts:
                time.sleep(min(0.1 * attempt, 0.3))

    return _evidence(
        request,
        status=IngestionStatus.FAILED,
        admission_status=admission.status,
        attempt_count=request.max_attempts,
        network_used=True,
        rationale="Provider request failed after bounded retries.",
        findings=("provider-request-failed", last_error[:160]),
    )


def _validate_endpoint(request: ProductionIngestionRequest) -> str | None:
    parsed = urlparse(request.endpoint_url)
    if parsed.scheme != "https":
        return "https-required"
    if parsed.hostname != _ALLOWED_HOSTS.get(request.provider_id):
        return "host-not-allowed"
    prefixes = _ALLOWED_PATH_PREFIXES.get(request.provider_id, ())
    if not any(parsed.path.startswith(prefix) for prefix in prefixes):
        return "path-not-allowed"
    return None


def _urllib_transport(request: ProductionIngestionRequest) -> bytes:
    headers = {"Accept": "application/json"}
    if request.user_agent:
        headers["User-Agent"] = request.user_agent
    http_request = urllib.request.Request(request.endpoint_url, headers=headers)
    try:
        with urllib.request.urlopen(
            http_request,
            timeout=request.timeout_seconds,
        ) as response:
            return response.read(request.max_response_bytes + 1)
    except urllib.error.URLError as exc:
        raise OSError(str(exc)) from exc


def _retain_success(
    request: ProductionIngestionRequest,
    payload: bytes,
    attempt_count: int,
) -> ProductionIngestionEvidence:
    digest = hashlib.sha256(payload).hexdigest()
    root = Path(request.storage_root).resolve()
    directory = root / "production-ingestion" / request.provider_id.value / request.resource_id
    directory.mkdir(parents=True, exist_ok=True)
    stem = str(request.request_id)
    payload_path = directory / f"{stem}.json"
    metadata_path = directory / f"{stem}.metadata.json"
    payload_tmp = payload_path.with_suffix(".json.tmp")
    metadata_tmp = metadata_path.with_suffix(".json.tmp")
    payload_tmp.write_bytes(payload)
    evidence = _evidence(
        request,
        status=IngestionStatus.SUCCEEDED,
        admission_status=AdmissionStatus.APPROVED,
        payload_uri=payload_path.as_uri(),
        metadata_uri=metadata_path.as_uri(),
        payload_sha256=f"sha256:{digest}",
        response_bytes=len(payload),
        attempt_count=attempt_count,
        network_used=True,
        cache_state="retained",
        rationale="Provider payload retained with admission and lineage evidence.",
        findings=("internal-use-only", "redistribution-disabled"),
    )
    metadata_tmp.write_text(evidence.model_dump_json(indent=2), encoding="utf-8")
    payload_tmp.replace(payload_path)
    metadata_tmp.replace(metadata_path)
    return evidence


def _evidence(
    request: ProductionIngestionRequest,
    *,
    status: IngestionStatus,
    admission_status: AdmissionStatus,
    rationale: str,
    findings: tuple[str, ...] = (),
    payload_uri: str | None = None,
    metadata_uri: str | None = None,
    payload_sha256: str | None = None,
    response_bytes: int = 0,
    attempt_count: int = 0,
    network_used: bool = False,
    cache_state: str = "not_applicable",
) -> ProductionIngestionEvidence:
    return ProductionIngestionEvidence(
        request_id=request.request_id,
        provider_id=request.provider_id,
        resource_id=request.resource_id,
        status=status,
        admission_status=admission_status,
        endpoint_url=request.endpoint_url,
        payload_uri=payload_uri,
        metadata_uri=metadata_uri,
        payload_sha256=payload_sha256,
        response_bytes=response_bytes,
        attempt_count=attempt_count,
        network_used=network_used,
        cache_state=cache_state,
        rationale=rationale,
        findings=findings,
    )
