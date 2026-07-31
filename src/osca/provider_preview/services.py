import json
import time
from collections.abc import Callable, Mapping
from hashlib import sha256
from pathlib import Path
from typing import Protocol, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from osca.provider_adapters import ProviderAdapterEndpoint
from osca.provider_catalog import ProviderCatalogIdentifier
from osca.provider_preview.contracts import (
    FredPreviewRequest,
    ProviderPreviewEvidence,
    ProviderPreviewMode,
    ProviderPreviewOutcome,
    SecPreviewRequest,
)


class ProviderPreviewError(RuntimeError):
    pass


class ProviderPreviewTransport(Protocol):
    def get(
        self,
        *,
        url: str,
        headers: Mapping[str, str],
        timeout_seconds: float,
        max_response_bytes: int,
    ) -> bytes: ...


class UrllibProviderPreviewTransport:
    def get(
        self,
        *,
        url: str,
        headers: Mapping[str, str],
        timeout_seconds: float,
        max_response_bytes: int,
    ) -> bytes:
        _validate_sec_source_uri(url)
        request = Request(url, headers=dict(headers), method="GET")
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                content_length = response.headers.get("Content-Length")
                if content_length is not None and int(content_length) > max_response_bytes:
                    raise ProviderPreviewError(
                        "SEC preview response exceeds configured byte limit"
                    )
                payload = response.read(max_response_bytes + 1)
        except HTTPError as exc:
            raise ProviderPreviewError(
                f"SEC preview request failed with HTTP status {exc.code}"
            ) from exc
        except URLError as exc:
            raise ProviderPreviewError("SEC preview request failed") from exc
        if len(payload) > max_response_bytes:
            raise ProviderPreviewError(
                "SEC preview response exceeds configured byte limit"
            )
        return payload


class SecFairAccessGate:
    def __init__(
        self,
        *,
        requests_per_second: float = 2.0,
        monotonic: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if requests_per_second <= 0.0 or requests_per_second > 9.0:
            raise ValueError(
                "SEC preview request rate must be greater than zero and at most 9 rps"
            )
        self._minimum_interval = 1.0 / requests_per_second
        self._monotonic = monotonic
        self._sleeper = sleeper
        self._last_request_at: float | None = None

    def wait(self) -> None:
        now = self._monotonic()
        if self._last_request_at is not None:
            elapsed = now - self._last_request_at
            remaining = self._minimum_interval - elapsed
            if remaining > 0.0:
                self._sleeper(remaining)
                now = self._monotonic()
        self._last_request_at = now


class SecPreviewService:
    def __init__(
        self,
        *,
        transport: ProviderPreviewTransport | None = None,
        fair_access_gate: SecFairAccessGate | None = None,
    ) -> None:
        self._transport = transport or UrllibProviderPreviewTransport()
        self._fair_access_gate = fair_access_gate or SecFairAccessGate()

    def run(
        self,
        request: SecPreviewRequest,
        *,
        storage_root: Path,
    ) -> ProviderPreviewEvidence:
        if request.fixture_path is not None:
            payload = _read_bounded_payload(
                request.fixture_path,
                max_response_bytes=request.max_response_bytes,
            )
            source_uri = request.fixture_path.resolve().as_uri()
            payload_uri = source_uri
            metadata_uri = None
            mode = ProviderPreviewMode.FIXTURE_REPLAY
            outcome = ProviderPreviewOutcome.SUCCEEDED
            cache_hit = False
            network_access_used = False
        else:
            source_uri = _sec_source_uri(request)
            cache_path = _sec_cache_path(storage_root, request)
            metadata_path = cache_path.with_suffix(".metadata.json")
            if cache_path.exists() and not request.force_refresh:
                payload = _read_bounded_payload(
                    cache_path,
                    max_response_bytes=request.max_response_bytes,
                )
                outcome = ProviderPreviewOutcome.CACHE_HIT
                cache_hit = True
                network_access_used = False
            else:
                self._fair_access_gate.wait()
                payload = self._transport.get(
                    url=source_uri,
                    headers={
                        "Accept": "application/json",
                        "User-Agent": cast(str, request.user_agent),
                    },
                    timeout_seconds=request.timeout_seconds,
                    max_response_bytes=request.max_response_bytes,
                )
                _write_atomic(cache_path, payload)
                outcome = ProviderPreviewOutcome.SUCCEEDED
                cache_hit = False
                network_access_used = True
            payload_uri = cache_path.resolve().as_uri()
            metadata_uri = metadata_path.resolve().as_uri()
            mode = ProviderPreviewMode.LIVE_PREVIEW

        document = _decode_json_object(payload)
        record_count = _sec_record_count(request.endpoint, document)
        digest = sha256(payload).hexdigest()
        evidence = ProviderPreviewEvidence(
            request_id=request.request_id,
            provider_id=ProviderCatalogIdentifier.SEC_EDGAR,
            endpoint=request.endpoint,
            mode=mode,
            outcome=outcome,
            resource_id=f"CIK{request.normalized_cik}",
            source_uri=source_uri,
            payload_uri=payload_uri,
            metadata_uri=metadata_uri,
            payload_sha256=digest,
            record_count=record_count,
            cache_hit=cache_hit,
            network_access_used=network_access_used,
            network_access_enabled=request.network_access_enabled,
            rationale=(
                "SEC preview payload replayed from a deterministic fixture."
                if mode is ProviderPreviewMode.FIXTURE_REPLAY
                else (
                    "SEC preview payload resolved from the bounded local cache."
                    if cache_hit
                    else "SEC preview payload retrieved through explicit opt-in network access."
                )
            ),
            finding_ids=(),
        )
        if metadata_uri is not None:
            _write_atomic(
                Path(urlparse(metadata_uri).path),
                json.dumps(
                    evidence.model_dump(mode="json"),
                    indent=2,
                    sort_keys=True,
                ).encode("utf-8"),
            )
        return evidence


def evaluate_fred_preview(request: FredPreviewRequest) -> ProviderPreviewEvidence:
    findings = [
        "fred-live-preview-policy-blocked",
        "fred-content-retention-not-permitted",
        "fred-software-ai-use-needs-legal-evidence",
    ]
    if request.secret_reference is not None:
        findings.append("fred-secret-reference-not-resolved")
    return ProviderPreviewEvidence(
        request_id=request.request_id,
        provider_id=ProviderCatalogIdentifier.FRED,
        endpoint=ProviderAdapterEndpoint.FRED_SERIES_OBSERVATIONS,
        mode=ProviderPreviewMode.POLICY_BLOCKED,
        outcome=ProviderPreviewOutcome.BLOCKED,
        resource_id=request.series_id,
        record_count=0,
        cache_hit=False,
        network_access_used=False,
        network_access_enabled=request.network_access_enabled,
        rationale=(
            "FRED live preview remains policy-blocked because current terms require "
            "separate legal evidence for software use and prohibit storing, caching, "
            "or archiving API content. No credential reference is resolved."
        ),
        finding_ids=tuple(findings),
    )


def _sec_source_uri(request: SecPreviewRequest) -> str:
    if request.endpoint is ProviderAdapterEndpoint.SEC_COMPANY_FACTS:
        uri = (
            "https://data.sec.gov/api/xbrl/companyfacts/"
            f"CIK{request.normalized_cik}.json"
        )
    else:
        uri = f"https://data.sec.gov/submissions/CIK{request.normalized_cik}.json"
    _validate_sec_source_uri(uri)
    return uri


def _validate_sec_source_uri(uri: str) -> None:
    parsed = urlparse(uri)
    if parsed.scheme != "https" or parsed.hostname != "data.sec.gov":
        raise ProviderPreviewError("SEC preview source must use approved HTTPS host")
    if not (
        parsed.path.startswith("/api/xbrl/companyfacts/CIK")
        or parsed.path.startswith("/submissions/CIK")
    ):
        raise ProviderPreviewError("SEC preview source path is not approved")


def _sec_cache_path(storage_root: Path, request: SecPreviewRequest) -> Path:
    return (
        storage_root
        / "provider-preview"
        / "sec-edgar"
        / request.endpoint.value
        / f"CIK{request.normalized_cik}.json"
    )


def _read_bounded_payload(path: Path, *, max_response_bytes: int) -> bytes:
    if not path.is_file():
        raise ProviderPreviewError(f"preview payload does not exist: {path}")
    if path.stat().st_size > max_response_bytes:
        raise ProviderPreviewError("preview payload exceeds configured byte limit")
    payload = path.read_bytes()
    if len(payload) > max_response_bytes:
        raise ProviderPreviewError("preview payload exceeds configured byte limit")
    return payload


def _write_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f".{path.name}.tmp")
    temporary_path.write_bytes(payload)
    temporary_path.replace(path)


def _decode_json_object(payload: bytes) -> dict[str, object]:
    try:
        decoded: object = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProviderPreviewError("preview payload is not valid UTF-8 JSON") from exc
    if not isinstance(decoded, dict):
        raise ProviderPreviewError("preview payload must be a JSON object")
    return cast(dict[str, object], decoded)


def _sec_record_count(
    endpoint: ProviderAdapterEndpoint,
    document: dict[str, object],
) -> int:
    if endpoint is ProviderAdapterEndpoint.SEC_COMPANY_FACTS:
        facts = document.get("facts")
        if not isinstance(facts, dict):
            raise ProviderPreviewError("SEC company-facts payload is missing facts")
        count = 0
        for taxonomy_value in facts.values():
            if isinstance(taxonomy_value, dict):
                count += len(taxonomy_value)
        return count

    filings = document.get("filings")
    if not isinstance(filings, dict):
        raise ProviderPreviewError("SEC submissions payload is missing filings")
    recent = filings.get("recent")
    if not isinstance(recent, dict):
        raise ProviderPreviewError("SEC submissions payload is missing recent filings")
    accession_numbers = recent.get("accessionNumber")
    if not isinstance(accession_numbers, list):
        raise ProviderPreviewError(
            "SEC submissions payload is missing accession numbers"
        )
    return len(accession_numbers)
