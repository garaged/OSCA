from __future__ import annotations

import csv
import hashlib
import json
import threading
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import unquote, urlencode, urlparse

import typer
from pydantic import BaseModel, ConfigDict, Field

from osca.local_data_import import (
    LocalOHLCVImportFormat,
    LocalOHLCVImportRequest,
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
    POLICY_BLOCKED = "policy_blocked"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    FAILED = "failed"


class HistoricalAcquisitionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.historical-acquisition.request"] = (
        "osca.historical-acquisition.request"
    )
    version: Literal["1.0.0"] = "1.0.0"
    provider_id: ProductionProvider
    asset_class: HistoricalAssetClass
    symbol: str = Field(min_length=1, max_length=80)
    timeframe: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
    storage_root: str = Field(min_length=1, max_length=2048)
    network_access_enabled: bool = False
    since: int | None = Field(default=None, ge=0)
    parser_version: str = Field(default="kraken-ohlc-v1", min_length=1, max_length=80)
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class HistoricalAcquisitionEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.historical-acquisition.evidence"] = (
        "osca.historical-acquisition.evidence"
    )
    version: Literal["1.0.0"] = "1.0.0"
    status: HistoricalAcquisitionStatus
    provider_id: ProductionProvider
    asset_class: HistoricalAssetClass
    symbol: str
    timeframe: str
    parser_version: str
    admission_status: AdmissionStatus
    ingestion_evidence_uri: str | None = None
    raw_payload_uri: str | None = None
    raw_payload_sha256: str | None = None
    dataset_revision_id: str | None = None
    canonical_payload_uri: str | None = None
    canonical_metadata_uri: str | None = None
    canonical_row_count: int | None = None
    source_attribution: str
    internal_use_only: bool = True
    redistribution_enabled: bool = False
    recommendations_enabled: bool = False
    broker_execution_enabled: bool = False
    real_capital_execution_enabled: bool = False
    rationale: str
    findings: tuple[str, ...] = ()
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


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
        if retained is not None:
            return retained
        return _run_historical_acquisition(request, transport=transport)


def _run_historical_acquisition(
    request: HistoricalAcquisitionRequest,
    *,
    transport: Transport | None,
) -> HistoricalAcquisitionEvidence:
    admission = admission_for(request.provider_id)
    if request.asset_class is HistoricalAssetClass.EQUITY:
        return _retain_acquisition_evidence(
            request,
            _base_evidence(
                request,
                status=HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE,
                admission_status=admission.status,
                source_attribution=request.provider_id.value,
                rationale=(
                    "No no-cost equity provider is admitted for OSCA workspace display, "
                    "retention, export, and backup. Use governed CSV import."
                ),
                findings=(
                    "equity-provider-not-admitted",
                    "csv-import-remains-supported",
                ),
            ),
        )

    if request.provider_id is not ProductionProvider.KRAKEN:
        return _retain_acquisition_evidence(
            request,
            _base_evidence(
                request,
                status=HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE,
                admission_status=admission.status,
                source_attribution=request.provider_id.value,
                rationale="Requested provider is not admitted for no-cost crypto OHLC.",
                findings=("provider-not-admitted-for-asset-class",),
            ),
        )

    query = {"pair": request.symbol, "interval": _KRAKEN_INTERVALS[request.timeframe]}
    if request.since is not None:
        query["since"] = request.since
    endpoint = "https://api.kraken.com/0/public/OHLC?" + urlencode(query)
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
    status = {
        IngestionStatus.SUCCEEDED: HistoricalAcquisitionStatus.SUCCEEDED,
        IngestionStatus.POLICY_BLOCKED: HistoricalAcquisitionStatus.POLICY_BLOCKED,
        IngestionStatus.PROVIDER_UNAVAILABLE: HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE,
        IngestionStatus.FAILED: HistoricalAcquisitionStatus.FAILED,
    }[ingestion.status]
    evidence = _base_evidence(
        request,
        status=status,
        admission_status=ingestion.admission_status,
        source_attribution="Kraken public spot OHLC",
        rationale=ingestion.rationale,
        findings=ingestion.findings,
        raw_payload_uri=ingestion.payload_uri,
        raw_payload_sha256=ingestion.payload_sha256,
    )
    if ingestion.status is not IngestionStatus.SUCCEEDED:
        return _retain_acquisition_evidence(request, evidence)

    try:
        canonical = _normalize_kraken_payload(request, ingestion.payload_uri)
    except KrakenUnavailableError as exc:
        evidence = evidence.model_copy(
            update={
                "status": HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE,
                "rationale": str(exc),
                "findings": (*evidence.findings, exc.finding, "retry-later"),
            }
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        evidence = evidence.model_copy(
            update={
                "status": HistoricalAcquisitionStatus.FAILED,
                "rationale": f"Canonical normalization failed: {exc}",
                "findings": (*evidence.findings, "canonical-normalization-failed"),
            }
        )
    else:
        evidence = evidence.model_copy(
            update={
                "dataset_revision_id": str(canonical.dataset_revision_id),
                "canonical_payload_uri": canonical.payload_uri,
                "canonical_metadata_uri": canonical.metadata_uri,
                "canonical_row_count": canonical.row_count,
                "rationale": "Provider payload normalized into a canonical OHLCV revision.",
                "findings": (*evidence.findings, "current-uncommitted-bar-excluded"),
            }
        )
    return _retain_acquisition_evidence(request, evidence)


class KrakenUnavailableError(ValueError):
    def __init__(self, message: str, finding: str) -> None:
        super().__init__(message)
        self.finding = finding


def _normalize_kraken_payload(
    request: HistoricalAcquisitionRequest,
    payload_uri: str | None,
):
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
            )
        if any("service" in str(item).lower() for item in errors):
            raise KrakenUnavailableError(
                f"Kraken service is unavailable: {text}",
                "provider-service-unavailable",
            )
        raise ValueError(f"Kraken response contained provider errors: {text}")
    result = document.get("result")
    if not isinstance(result, dict):
        raise ValueError("Kraken response result must be an object")
    pair_keys = [key for key in result if key != "last"]
    if len(pair_keys) != 1:
        raise ValueError("Kraken response must contain exactly one pair series")
    rows = result[pair_keys[0]]
    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError("Kraken response requires one completed bar and one current bar")
    completed_rows = rows[:-1]
    csv_path = _canonical_source_path(request)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "parser_version",
            ]
        )
        for row in completed_rows:
            if not isinstance(row, list) or len(row) < 7:
                raise ValueError("Kraken OHLC row must contain at least seven fields")
            timestamp = datetime.fromtimestamp(int(row[0]), tz=UTC).isoformat()
            writer.writerow(
                [timestamp, row[1], row[2], row[3], row[4], row[6], request.parser_version]
            )
    return import_local_ohlcv(
        LocalOHLCVImportRequest(
            input_path=str(csv_path),
            storage_root=request.storage_root,
            symbol=request.symbol,
            timeframe=LocalOHLCVTimeframe(request.timeframe),
            input_format=LocalOHLCVImportFormat.CSV,
            source_uri=f"provider://kraken/spot_ohlc/{request.parser_version}",
            calendar_assumption="continuous-crypto-market",
        )
    )


def _request_key(request: HistoricalAcquisitionRequest) -> str:
    identity = (
        f"{request.provider_id.value}|{request.asset_class.value}|{request.symbol}|"
        f"{request.timeframe}|{request.since}|{request.parser_version}"
    )
    return hashlib.sha256(identity.encode()).hexdigest()


def _lock_for(key: str) -> threading.Lock:
    with _LOCKS_GUARD:
        return _REQUEST_LOCKS.setdefault(key, threading.Lock())


def _evidence_path(request: HistoricalAcquisitionRequest) -> Path:
    root = Path(request.storage_root).resolve() / "historical-acquisition"
    symbol = request.symbol.replace("/", "_")
    since = "all" if request.since is None else str(request.since)
    parser = request.parser_version.replace("/", "_")
    stem = (
        f"{request.provider_id.value}-{request.asset_class.value}-"
        f"{symbol}-{request.timeframe}-{since}-{parser}"
    )
    return root / f"{stem}.json"


def _load_reusable_evidence(
    request: HistoricalAcquisitionRequest,
) -> HistoricalAcquisitionEvidence | None:
    path = _evidence_path(request)
    if not path.is_file():
        return None
    evidence = HistoricalAcquisitionEvidence.model_validate_json(
        path.read_text(encoding="utf-8")
    )
    if evidence.status is not HistoricalAcquisitionStatus.SUCCEEDED:
        return None
    required = (evidence.canonical_payload_uri, evidence.canonical_metadata_uri)
    if not all(required):
        return None
    if not all(Path(value).is_file() for value in required if value is not None):
        return None
    return evidence


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
    *,
    status: HistoricalAcquisitionStatus,
    admission_status: AdmissionStatus,
    source_attribution: str,
    rationale: str,
    findings: tuple[str, ...],
    raw_payload_uri: str | None = None,
    raw_payload_sha256: str | None = None,
) -> HistoricalAcquisitionEvidence:
    return HistoricalAcquisitionEvidence(
        status=status,
        provider_id=request.provider_id,
        asset_class=request.asset_class,
        symbol=request.symbol,
        timeframe=request.timeframe,
        parser_version=request.parser_version,
        admission_status=admission_status,
        raw_payload_uri=raw_payload_uri,
        raw_payload_sha256=raw_payload_sha256,
        source_attribution=source_attribution,
        rationale=rationale,
        findings=findings,
    )


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
    network_access_enabled: Annotated[
        bool, typer.Option("--network-access-enabled")
    ] = False,
    since: Annotated[int | None, typer.Option("--since")] = None,
    parser_version: Annotated[
        str, typer.Option("--parser-version")
    ] = "kraken-ohlc-v1",
) -> None:
    """Fetch Kraken crypto OHLC or retain an explicit blocked equity decision."""

    evidence = run_historical_acquisition(
        HistoricalAcquisitionRequest(
            provider_id=provider,
            asset_class=asset_class,
            symbol=symbol,
            timeframe=timeframe,
            storage_root=str(storage_root),
            network_access_enabled=network_access_enabled,
            since=since,
            parser_version=parser_version,
        )
    )
    typer.echo(json.dumps(evidence.model_dump(mode="json"), indent=2, sort_keys=True))
    if evidence.status not in {
        HistoricalAcquisitionStatus.SUCCEEDED,
        HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE,
    }:
        raise typer.Exit(1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
