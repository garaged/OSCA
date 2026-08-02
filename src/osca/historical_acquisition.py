from __future__ import annotations

import csv
import hashlib
import json
import threading
import time
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal, Self
from urllib.parse import unquote, urlencode, urlparse
from uuid import NAMESPACE_URL, UUID, uuid5

import typer
from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.local_data_import import (
    LocalOHLCVImportFormat,
    LocalOHLCVImportRequest,
    LocalOHLCVImportResult,
    LocalOHLCVTimeframe,
    import_local_ohlcv,
)
from osca.production_ingestion.contracts import (
    AdmissionStatus,
    IngestionStatus,
    ProductionIngestionRequest,
    ProductionProvider,
)
from osca.production_ingestion.policy import admission_for
from osca.production_ingestion.services import Transport, run_production_ingestion


class HistoricalAssetClass(StrEnum):
    EQUITY = "equity"
    CRYPTO = "crypto"


class HistoricalAcquisitionStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FRESH = "fresh"
    STALE = "stale"
    PARTIAL = "partial"
    INVALID = "invalid"
    CORRUPT = "corrupt"
    REFRESHING = "refreshing"
    QUOTA_BLOCKED = "quota_blocked"
    CREDENTIAL_BLOCKED = "credential_blocked"
    POLICY_BLOCKED = "policy_blocked"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    CANCELLED = "cancelled"
    FAILED = "failed"


class AcquisitionJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    RECOVERING = "recovering"
    CANCELLED = "cancelled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class AcquisitionAttempt(BaseModel):
    model_config = ConfigDict(frozen=True)

    attempt: int = Field(ge=1)
    started_at: datetime
    completed_at: datetime
    outcome: str
    duration_ms: int = Field(ge=0)
    retryable: bool = False
    retry_after_seconds: int | None = Field(default=None, ge=0)


class HistoricalAcquisitionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.historical-acquisition.request"] = (
        "osca.historical-acquisition.request"
    )
    version: Literal["2.0.0"] = "2.0.0"
    provider_id: ProductionProvider
    asset_class: HistoricalAssetClass
    symbol: str = Field(min_length=1, max_length=80)
    timeframe: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
    storage_root: str = Field(min_length=1, max_length=4096)
    venue_context: str = Field(default="kraken-spot", min_length=1, max_length=160)
    expected_pair_key: str | None = Field(default=None, min_length=1, max_length=160)
    start_at: datetime | None = None
    end_at: datetime | None = None
    freshness_max_age_seconds: int | None = Field(default=None, ge=0)
    minimum_rows: int = Field(default=1, ge=1)
    require_complete_range: bool = False
    network_access_enabled: bool = False
    cancel_requested: bool = False
    since: int | None = Field(default=None, ge=0)
    parser_version: str = Field(default="kraken-ohlc-v1", min_length=1, max_length=80)
    normalizer_version: str = Field(default="canonical-ohlcv-v1", min_length=1, max_length=80)
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        for value in (self.start_at, self.end_at, self.requested_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("acquisition timestamps must be timezone-aware")
        if self.start_at and self.end_at and self.start_at >= self.end_at:
            raise ValueError("start_at must be earlier than end_at")
        if self.asset_class is HistoricalAssetClass.CRYPTO and not self.venue_context:
            raise ValueError("crypto acquisition requires venue context")
        return self


class HistoricalAcquisitionEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.historical-acquisition.evidence"] = (
        "osca.historical-acquisition.evidence"
    )
    version: Literal["2.0.0"] = "2.0.0"
    acquisition_id: UUID
    request_id: UUID
    correlation_id: UUID
    job_id: UUID
    job_status: AcquisitionJobStatus
    status: HistoricalAcquisitionStatus
    provider_id: ProductionProvider
    asset_class: HistoricalAssetClass
    symbol: str
    timeframe: str
    venue_context: str
    provider_pair_key: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    parser_version: str
    normalizer_version: str
    admission_status: AdmissionStatus
    ingestion_evidence_uri: str | None = None
    job_evidence_uri: str | None = None
    raw_payload_uri: str | None = None
    raw_payload_sha256: str | None = None
    normalized_sha256: str | None = None
    dataset_revision_id: str | None = None
    predecessor_revision_id: str | None = None
    supersedes_revision_id: str | None = None
    correction_reason: str | None = None
    canonical_payload_uri: str | None = None
    canonical_metadata_uri: str | None = None
    canonical_row_count: int | None = None
    source_attribution: str
    quota_state: str = "not_reported"
    retry_after_seconds: int | None = None
    attempts: tuple[AcquisitionAttempt, ...] = ()
    reuse_state: Literal["new", "reused", "recovered"] = "new"
    progress_percent: int = Field(default=100, ge=0, le=100)
    duration_ms: int = Field(default=0, ge=0)
    internal_use_only: bool = True
    redistribution_enabled: bool = False
    recommendations_enabled: bool = False
    broker_execution_enabled: bool = False
    real_capital_execution_enabled: bool = False
    rationale: str
    remediation: tuple[str, ...] = ()
    findings: tuple[str, ...] = ()
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AcquisitionJobRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.historical-acquisition.job"] = "osca.historical-acquisition.job"
    version: Literal["1.0.0"] = "1.0.0"
    job_id: UUID
    request_id: UUID
    correlation_id: UUID
    request_key: str
    status: AcquisitionJobStatus
    progress_percent: int = Field(ge=0, le=100)
    stage: str
    cancel_requested: bool = False
    attempt_count: int = Field(default=0, ge=0)
    started_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    last_error: str | None = None


_KRAKEN_INTERVALS = {
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "1h": 60,
    "4h": 240,
    "1d": 1440,
}
_LOCKS_GUARD = threading.Lock()
_REQUEST_LOCKS: dict[str, threading.Lock] = {}


def run_historical_acquisition(
    request: HistoricalAcquisitionRequest,
    *,
    transport: Transport | None = None,
) -> HistoricalAcquisitionEvidence:
    key = _request_key(request)
    with _lock_for(key):
        retained = _load_reusable_evidence(request)
        if retained is not None and not request.cancel_requested:
            return retained.model_copy(update={"reuse_state": "reused"})
        job, recovered = _start_or_recover_job(request, key)
        if request.cancel_requested:
            cancelled = _base_evidence(
                request,
                job,
                status=HistoricalAcquisitionStatus.CANCELLED,
                job_status=AcquisitionJobStatus.CANCELLED,
                admission_status=admission_for(request.provider_id).status,
                source_attribution=request.provider_id.value,
                rationale="Acquisition was cancelled before provider retrieval.",
                remediation=("Submit the same request without --cancel-requested to retry.",),
                findings=("cancelled-before-network",),
                reuse_state="recovered" if recovered else "new",
            )
            _finish_job(request, job, AcquisitionJobStatus.CANCELLED, "cancelled", None)
            return _retain_acquisition_evidence(request, cancelled)
        return _run_historical_acquisition(
            request,
            job=job,
            recovered=recovered,
            transport=transport,
        )


def _run_historical_acquisition(
    request: HistoricalAcquisitionRequest,
    *,
    job: AcquisitionJobRecord,
    recovered: bool,
    transport: Transport | None,
) -> HistoricalAcquisitionEvidence:
    started = time.monotonic()
    admission = admission_for(request.provider_id)
    _update_job(request, job, AcquisitionJobStatus.RUNNING, 10, "policy-resolution")
    if request.asset_class is HistoricalAssetClass.EQUITY:
        evidence = _base_evidence(
            request,
            job,
            status=HistoricalAcquisitionStatus.POLICY_BLOCKED,
            job_status=AcquisitionJobStatus.FAILED,
            admission_status=admission.status,
            source_attribution=request.provider_id.value,
            rationale=(
                "No no-cost equity provider is admitted for OSCA workspace display, "
                "retention, export, and backup. Use governed CSV import."
            ),
            remediation=("Use osca local-ohlcv-import with a governed CSV file.",),
            findings=("equity-provider-not-admitted", "csv-import-remains-supported"),
            reuse_state="recovered" if recovered else "new",
        )
        return _complete(request, job, evidence, started)

    if request.provider_id is not ProductionProvider.KRAKEN:
        evidence = _base_evidence(
            request,
            job,
            status=HistoricalAcquisitionStatus.POLICY_BLOCKED,
            job_status=AcquisitionJobStatus.FAILED,
            admission_status=admission.status,
            source_attribution=request.provider_id.value,
            rationale="Requested provider is not admitted for no-cost crypto OHLC.",
            remediation=("Select kraken or use governed CSV import.",),
            findings=("provider-not-admitted-for-asset-class",),
            reuse_state="recovered" if recovered else "new",
        )
        return _complete(request, job, evidence, started)

    query: dict[str, str | int] = {
        "pair": request.symbol,
        "interval": _KRAKEN_INTERVALS[request.timeframe],
    }
    since = request.since
    if request.start_at is not None:
        since = int(request.start_at.timestamp())
    if since is not None:
        query["since"] = since
    endpoint = "https://api.kraken.com/0/public/OHLC?" + urlencode(query)
    _update_job(request, job, AcquisitionJobStatus.RUNNING, 30, "provider-retrieval")
    attempt_started = datetime.now(UTC)
    attempt_clock = time.monotonic()
    ingestion = run_production_ingestion(
        ProductionIngestionRequest(
            provider_id=ProductionProvider.KRAKEN,
            resource_id="spot_ohlc",
            endpoint_url=endpoint,
            storage_root=request.storage_root,
            network_access_enabled=request.network_access_enabled,
        ),
        transport=transport,
    )
    attempt = AcquisitionAttempt(
        attempt=max(1, ingestion.attempt_count),
        started_at=attempt_started,
        completed_at=datetime.now(UTC),
        outcome=ingestion.status.value,
        duration_ms=int((time.monotonic() - attempt_clock) * 1000),
        retryable=ingestion.status is IngestionStatus.PROVIDER_UNAVAILABLE,
    )
    status = {
        IngestionStatus.SUCCEEDED: HistoricalAcquisitionStatus.REFRESHING,
        IngestionStatus.POLICY_BLOCKED: HistoricalAcquisitionStatus.POLICY_BLOCKED,
        IngestionStatus.PROVIDER_UNAVAILABLE: HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE,
        IngestionStatus.FAILED: HistoricalAcquisitionStatus.FAILED,
    }[ingestion.status]
    evidence = _base_evidence(
        request,
        job,
        status=status,
        job_status=(
            AcquisitionJobStatus.RUNNING
            if ingestion.status is IngestionStatus.SUCCEEDED
            else AcquisitionJobStatus.FAILED
        ),
        admission_status=ingestion.admission_status,
        source_attribution="Kraken public spot OHLC",
        rationale=ingestion.rationale,
        remediation=("Retry after provider recovery.",),
        findings=ingestion.findings,
        raw_payload_uri=ingestion.payload_uri,
        raw_payload_sha256=ingestion.payload_sha256,
        attempts=(attempt,),
        reuse_state="recovered" if recovered else "new",
    )
    if ingestion.status is not IngestionStatus.SUCCEEDED:
        return _complete(request, job, evidence, started)

    _update_job(request, job, AcquisitionJobStatus.RUNNING, 65, "normalization")
    try:
        normalized = _normalize_kraken_payload(request, ingestion.payload_uri)
    except KrakenUnavailableError as exc:
        evidence = evidence.model_copy(
            update={
                "status": exc.status,
                "job_status": AcquisitionJobStatus.FAILED,
                "quota_state": exc.quota_state,
                "retry_after_seconds": exc.retry_after_seconds,
                "rationale": str(exc),
                "remediation": ("Retry after the indicated provider recovery window.",),
                "findings": (*evidence.findings, exc.finding),
            }
        )
    except json.JSONDecodeError as exc:
        evidence = evidence.model_copy(
            update={
                "status": HistoricalAcquisitionStatus.CORRUPT,
                "job_status": AcquisitionJobStatus.FAILED,
                "rationale": f"Provider payload was not valid JSON: {exc}",
                "remediation": ("Retry retrieval; do not use the retained corrupt payload.",),
                "findings": (*evidence.findings, "provider-payload-corrupt"),
            }
        )
    except (OSError, ValueError) as exc:
        evidence = evidence.model_copy(
            update={
                "status": HistoricalAcquisitionStatus.INVALID,
                "job_status": AcquisitionJobStatus.FAILED,
                "rationale": f"Canonical normalization failed: {exc}",
                "remediation": ("Review symbol mapping, range, and provider response.",),
                "findings": (*evidence.findings, "canonical-normalization-invalid"),
            }
        )
    else:
        predecessor = _latest_predecessor(request, normalized.result.dataset_revision_id)
        final_status = _classify_completeness(request, normalized)
        evidence = evidence.model_copy(
            update={
                "status": final_status,
                "job_status": AcquisitionJobStatus.SUCCEEDED,
                "provider_pair_key": normalized.provider_pair_key,
                "normalized_sha256": normalized.normalized_sha256,
                "dataset_revision_id": str(normalized.result.dataset_revision_id),
                "predecessor_revision_id": predecessor,
                "supersedes_revision_id": predecessor,
                "correction_reason": (
                    "parser-or-provider-correction" if predecessor is not None else None
                ),
                "canonical_payload_uri": normalized.result.payload_uri,
                "canonical_metadata_uri": normalized.result.metadata_uri,
                "canonical_row_count": normalized.result.row_count,
                "progress_percent": 100,
                "rationale": "Provider payload normalized into a canonical OHLCV revision.",
                "remediation": _remediation_for_status(final_status),
                "findings": (
                    *evidence.findings,
                    "current-uncommitted-bar-excluded",
                    *normalized.findings,
                ),
            }
        )
    return _complete(request, job, evidence, started)


class NormalizedKrakenResult(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    result: LocalOHLCVImportResult
    provider_pair_key: str
    normalized_sha256: str
    first_timestamp: datetime
    last_timestamp: datetime
    findings: tuple[str, ...] = ()


class KrakenUnavailableError(ValueError):
    def __init__(
        self,
        message: str,
        finding: str,
        *,
        status: HistoricalAcquisitionStatus,
        quota_state: str = "not_reported",
        retry_after_seconds: int | None = None,
    ) -> None:
        super().__init__(message)
        self.finding = finding
        self.status = status
        self.quota_state = quota_state
        self.retry_after_seconds = retry_after_seconds


def _normalize_kraken_payload(
    request: HistoricalAcquisitionRequest,
    payload_uri: str | None,
) -> NormalizedKrakenResult:
    if payload_uri is None:
        raise ValueError("successful ingestion did not retain a raw payload")
    payload_path = _path_from_uri(payload_uri)
    document = json.loads(payload_path.read_text(encoding="utf-8"))
    errors = document.get("error")
    if not isinstance(errors, list):
        raise ValueError("Kraken response error field must be a list")
    if errors:
        text = "; ".join(str(item) for item in errors)
        if any("rate limit" in str(item).lower() for item in errors):
            raise KrakenUnavailableError(
                f"Kraken rate limit blocked acquisition: {text}",
                "rate-limit-exceeded",
                status=HistoricalAcquisitionStatus.QUOTA_BLOCKED,
                quota_state="exhausted",
                retry_after_seconds=60,
            )
        if any("service" in str(item).lower() for item in errors):
            raise KrakenUnavailableError(
                f"Kraken service is unavailable: {text}",
                "provider-service-unavailable",
                status=HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE,
            )
        raise ValueError(f"Kraken response contained provider errors: {text}")
    result = document.get("result")
    if not isinstance(result, dict):
        raise ValueError("Kraken response result must be an object")
    pair_keys = [key for key in result if key != "last"]
    if len(pair_keys) != 1:
        raise ValueError("Kraken response must contain exactly one pair series")
    pair_key = str(pair_keys[0])
    if request.expected_pair_key and pair_key != request.expected_pair_key:
        raise ValueError(
            f"provider pair mapping mismatch: expected {request.expected_pair_key}, got {pair_key}"
        )
    rows = result[pair_key]
    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError("Kraken response requires one completed bar and one current bar")
    completed_rows = rows[:-1]
    filtered: list[list[object]] = []
    for raw_row in completed_rows:
        if not isinstance(raw_row, list) or len(raw_row) < 7:
            raise ValueError("Kraken OHLC row must contain at least seven fields")
        timestamp = datetime.fromtimestamp(int(raw_row[0]), tz=UTC)
        if request.start_at and timestamp < request.start_at:
            continue
        if request.end_at and timestamp >= request.end_at:
            continue
        filtered.append(raw_row)
    if not filtered:
        raise ValueError("provider response contains no completed rows in the requested range")
    csv_path = _canonical_source_path(request)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        for row in filtered:
            timestamp = datetime.fromtimestamp(int(row[0]), tz=UTC).isoformat()
            values = [timestamp, row[1], row[2], row[3], row[4], row[6]]
            writer.writerow(values)
            digest.update(("|".join(str(value) for value in values) + "\n").encode())
    imported = import_local_ohlcv(
        LocalOHLCVImportRequest(
            input_path=str(csv_path),
            storage_root=request.storage_root,
            symbol=request.symbol,
            timeframe=LocalOHLCVTimeframe(request.timeframe),
            input_format=LocalOHLCVImportFormat.CSV,
            source_uri=(
                f"provider://kraken/spot_ohlc/{pair_key}/"
                f"{request.parser_version}/{request.normalizer_version}"
            ),
            calendar_assumption="continuous-crypto-market",
        )
    )
    first = datetime.fromtimestamp(int(filtered[0][0]), tz=UTC)
    last = datetime.fromtimestamp(int(filtered[-1][0]), tz=UTC)
    findings: list[str] = []
    if len(filtered) < request.minimum_rows:
        findings.append("minimum-row-expectation-not-met")
    if request.start_at and first > request.start_at:
        findings.append("requested-range-start-not-covered")
    if request.end_at and last < request.end_at:
        findings.append("requested-range-end-not-covered")
    return NormalizedKrakenResult(
        result=imported,
        provider_pair_key=pair_key,
        normalized_sha256=f"sha256:{digest.hexdigest()}",
        first_timestamp=first,
        last_timestamp=last,
        findings=tuple(findings),
    )


def _classify_completeness(
    request: HistoricalAcquisitionRequest,
    normalized: NormalizedKrakenResult,
) -> HistoricalAcquisitionStatus:
    findings = set(normalized.findings)
    if "minimum-row-expectation-not-met" in findings:
        return HistoricalAcquisitionStatus.PARTIAL
    if request.require_complete_range and any("range" in value for value in findings):
        return HistoricalAcquisitionStatus.PARTIAL
    if request.freshness_max_age_seconds is not None:
        age = (datetime.now(UTC) - normalized.last_timestamp).total_seconds()
        if age > request.freshness_max_age_seconds:
            return HistoricalAcquisitionStatus.STALE
        return HistoricalAcquisitionStatus.FRESH
    return HistoricalAcquisitionStatus.SUCCEEDED


def _remediation_for_status(status: HistoricalAcquisitionStatus) -> tuple[str, ...]:
    if status is HistoricalAcquisitionStatus.PARTIAL:
        return ("Adjust the requested range or provider capability expectations.",)
    if status is HistoricalAcquisitionStatus.STALE:
        return ("Retry with network access when fresher data is required.",)
    return ()


def _request_key(request: HistoricalAcquisitionRequest) -> str:
    identity = request.model_dump(
        mode="json",
        exclude={"requested_at", "cancel_requested", "network_access_enabled"},
    )
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()


def _ids(request: HistoricalAcquisitionRequest) -> tuple[UUID, UUID, UUID, UUID]:
    key = _request_key(request)
    request_id = uuid5(NAMESPACE_URL, f"osca-request:{key}")
    correlation_id = uuid5(NAMESPACE_URL, f"osca-correlation:{key}")
    job_id = uuid5(NAMESPACE_URL, f"osca-job:{key}")
    acquisition_id = uuid5(NAMESPACE_URL, f"osca-acquisition:{key}")
    return request_id, correlation_id, job_id, acquisition_id


def _lock_for(key: str) -> threading.Lock:
    with _LOCKS_GUARD:
        return _REQUEST_LOCKS.setdefault(key, threading.Lock())


def _evidence_path(request: HistoricalAcquisitionRequest) -> Path:
    root = Path(request.storage_root).resolve() / "historical-acquisition"
    symbol = request.symbol.replace("/", "_")
    return root / f"{request.provider_id.value}-{request.asset_class.value}-{symbol}-{_request_key(request)}.json"


def _job_path(request: HistoricalAcquisitionRequest) -> Path:
    return Path(request.storage_root).resolve() / "historical-acquisition" / "jobs" / f"{_request_key(request)}.json"


def _start_or_recover_job(
    request: HistoricalAcquisitionRequest,
    key: str,
) -> tuple[AcquisitionJobRecord, bool]:
    path = _job_path(request)
    request_id, correlation_id, job_id, _ = _ids(request)
    recovered = False
    now = datetime.now(UTC)
    if path.is_file():
        previous = AcquisitionJobRecord.model_validate_json(path.read_text(encoding="utf-8"))
        if previous.status in {AcquisitionJobStatus.RUNNING, AcquisitionJobStatus.RECOVERING}:
            recovered = True
    job = AcquisitionJobRecord(
        job_id=job_id,
        request_id=request_id,
        correlation_id=correlation_id,
        request_key=key,
        status=AcquisitionJobStatus.RECOVERING if recovered else AcquisitionJobStatus.PENDING,
        progress_percent=0,
        stage="recovering" if recovered else "pending",
        started_at=now,
        updated_at=now,
    )
    _write_job(path, job)
    return job, recovered


def _update_job(
    request: HistoricalAcquisitionRequest,
    job: AcquisitionJobRecord,
    status: AcquisitionJobStatus,
    progress: int,
    stage: str,
) -> AcquisitionJobRecord:
    updated = job.model_copy(
        update={
            "status": status,
            "progress_percent": progress,
            "stage": stage,
            "attempt_count": job.attempt_count + (1 if stage == "provider-retrieval" else 0),
            "updated_at": datetime.now(UTC),
        }
    )
    _write_job(_job_path(request), updated)
    return updated


def _finish_job(
    request: HistoricalAcquisitionRequest,
    job: AcquisitionJobRecord,
    status: AcquisitionJobStatus,
    stage: str,
    error: str | None,
) -> None:
    finished = job.model_copy(
        update={
            "status": status,
            "progress_percent": 100,
            "stage": stage,
            "updated_at": datetime.now(UTC),
            "completed_at": datetime.now(UTC),
            "last_error": error,
        }
    )
    _write_job(_job_path(request), finished)


def _write_job(path: Path, job: AcquisitionJobRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(job.model_dump_json(indent=2) + "\n", encoding="utf-8")


def _load_reusable_evidence(
    request: HistoricalAcquisitionRequest,
) -> HistoricalAcquisitionEvidence | None:
    path = _evidence_path(request)
    if not path.is_file():
        return None
    evidence = HistoricalAcquisitionEvidence.model_validate_json(path.read_text(encoding="utf-8"))
    if evidence.status not in {
        HistoricalAcquisitionStatus.SUCCEEDED,
        HistoricalAcquisitionStatus.FRESH,
        HistoricalAcquisitionStatus.STALE,
        HistoricalAcquisitionStatus.PARTIAL,
    }:
        return None
    required = (evidence.canonical_payload_uri, evidence.canonical_metadata_uri)
    if not all(required):
        return None
    if not all(Path(value).is_file() for value in required if value is not None):
        return None
    return evidence


def _latest_predecessor(
    request: HistoricalAcquisitionRequest,
    revision_id: UUID,
) -> str | None:
    root = Path(request.storage_root).resolve() / "historical-acquisition"
    if not root.is_dir():
        return None
    candidates: list[HistoricalAcquisitionEvidence] = []
    for path in root.glob("*.json"):
        try:
            item = HistoricalAcquisitionEvidence.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if (
            item.provider_id == request.provider_id
            and item.symbol == request.symbol
            and item.timeframe == request.timeframe
            and item.dataset_revision_id
            and item.dataset_revision_id != str(revision_id)
        ):
            candidates.append(item)
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.completed_at).dataset_revision_id


def _canonical_source_path(request: HistoricalAcquisitionRequest) -> Path:
    root = Path(request.storage_root).resolve() / "historical-acquisition" / "normalized"
    return root / f"{_request_key(request)}.csv"


def _path_from_uri(uri: str) -> Path:
    parsed = urlparse(uri)
    if parsed.scheme == "file":
        return Path(unquote(parsed.path))
    return Path(uri)


def _base_evidence(
    request: HistoricalAcquisitionRequest,
    job: AcquisitionJobRecord,
    *,
    status: HistoricalAcquisitionStatus,
    job_status: AcquisitionJobStatus,
    admission_status: AdmissionStatus,
    source_attribution: str,
    rationale: str,
    remediation: tuple[str, ...],
    findings: tuple[str, ...],
    raw_payload_uri: str | None = None,
    raw_payload_sha256: str | None = None,
    attempts: tuple[AcquisitionAttempt, ...] = (),
    reuse_state: Literal["new", "reused", "recovered"] = "new",
) -> HistoricalAcquisitionEvidence:
    request_id, correlation_id, job_id, acquisition_id = _ids(request)
    return HistoricalAcquisitionEvidence(
        acquisition_id=acquisition_id,
        request_id=request_id,
        correlation_id=correlation_id,
        job_id=job_id,
        job_status=job_status,
        status=status,
        provider_id=request.provider_id,
        asset_class=request.asset_class,
        symbol=request.symbol,
        timeframe=request.timeframe,
        venue_context=request.venue_context,
        start_at=request.start_at,
        end_at=request.end_at,
        parser_version=request.parser_version,
        normalizer_version=request.normalizer_version,
        admission_status=admission_status,
        job_evidence_uri=_job_path(request).as_uri(),
        raw_payload_uri=raw_payload_uri,
        raw_payload_sha256=raw_payload_sha256,
        source_attribution=source_attribution,
        attempts=attempts,
        reuse_state=reuse_state,
        rationale=rationale,
        remediation=remediation,
        findings=findings,
    )


def _complete(
    request: HistoricalAcquisitionRequest,
    job: AcquisitionJobRecord,
    evidence: HistoricalAcquisitionEvidence,
    started: float,
) -> HistoricalAcquisitionEvidence:
    duration = int((time.monotonic() - started) * 1000)
    completed = evidence.model_copy(update={"duration_ms": duration, "progress_percent": 100})
    _finish_job(
        request,
        job,
        completed.job_status,
        "completed" if completed.job_status is AcquisitionJobStatus.SUCCEEDED else "failed",
        None if completed.job_status is AcquisitionJobStatus.SUCCEEDED else completed.rationale,
    )
    return _retain_acquisition_evidence(request, completed)


def _retain_acquisition_evidence(
    request: HistoricalAcquisitionRequest,
    evidence: HistoricalAcquisitionEvidence,
) -> HistoricalAcquisitionEvidence:
    path = _evidence_path(request)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = evidence.model_copy(update={"ingestion_evidence_uri": path.as_uri()})
    path.write_text(payload.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return payload


app = typer.Typer(help="Acquire governed no-cost historical OHLCV evidence.")


@app.command("fetch")
def fetch_historical(
    symbol: str,
    asset_class: HistoricalAssetClass,
    provider: ProductionProvider,
    timeframe: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"] = "1d",
    storage_root: Annotated[Path, typer.Option("--storage-root")] = Path(".osca"),
    network_access_enabled: Annotated[bool, typer.Option("--network-access-enabled")] = False,
    since: Annotated[int | None, typer.Option("--since")] = None,
    start_at: Annotated[datetime | None, typer.Option("--start-at")] = None,
    end_at: Annotated[datetime | None, typer.Option("--end-at")] = None,
    expected_pair_key: Annotated[str | None, typer.Option("--expected-pair-key")] = None,
    minimum_rows: Annotated[int, typer.Option("--minimum-rows")] = 1,
    require_complete_range: Annotated[bool, typer.Option("--require-complete-range")] = False,
    freshness_max_age_seconds: Annotated[
        int | None, typer.Option("--freshness-max-age-seconds")
    ] = None,
    cancel_requested: Annotated[bool, typer.Option("--cancel-requested")] = False,
    parser_version: Annotated[str, typer.Option("--parser-version")] = "kraken-ohlc-v1",
    normalizer_version: Annotated[
        str, typer.Option("--normalizer-version")
    ] = "canonical-ohlcv-v1",
) -> None:
    """Fetch governed Kraken OHLC or retain an explicit blocked-source decision."""
    evidence = run_historical_acquisition(
        HistoricalAcquisitionRequest(
            provider_id=provider,
            asset_class=asset_class,
            symbol=symbol,
            timeframe=timeframe,
            storage_root=str(storage_root),
            network_access_enabled=network_access_enabled,
            since=since,
            start_at=start_at,
            end_at=end_at,
            expected_pair_key=expected_pair_key,
            minimum_rows=minimum_rows,
            require_complete_range=require_complete_range,
            freshness_max_age_seconds=freshness_max_age_seconds,
            cancel_requested=cancel_requested,
            parser_version=parser_version,
            normalizer_version=normalizer_version,
        )
    )
    typer.echo(json.dumps(evidence.model_dump(mode="json"), indent=2, sort_keys=True))
    acceptable = {
        HistoricalAcquisitionStatus.SUCCEEDED,
        HistoricalAcquisitionStatus.FRESH,
        HistoricalAcquisitionStatus.STALE,
        HistoricalAcquisitionStatus.PARTIAL,
        HistoricalAcquisitionStatus.POLICY_BLOCKED,
    }
    if evidence.status not in acceptable:
        raise typer.Exit(1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
