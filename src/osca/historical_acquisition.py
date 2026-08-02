from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, Literal
from urllib.parse import unquote, urlencode, urlparse
from uuid import UUID

import typer
from pydantic import BaseModel, ConfigDict, Field

from osca.local_data_import import (
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
    admission_status: AdmissionStatus
    ingestion_evidence_uri: str | None = None
    raw_payload_uri: str | None = None
    raw_payload_sha256: str | None = None
    dataset_revision_id: UUID | None = None
    canonical_payload_uri: str | None = None
    canonical_metadata_uri: str | None = None
    canonical_row_count: int | None = Field(default=None, ge=1)
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
_TIMEFRAMES = {value.value: value for value in LocalOHLCVTimeframe}


def run_historical_acquisition(
    request: HistoricalAcquisitionRequest,
    *,
    transport: Transport | None = None,
) -> HistoricalAcquisitionEvidence:
    admission = admission_for(request.provider_id)
    if request.asset_class is HistoricalAssetClass.EQUITY:
        return _retain_acquisition_evidence(
            request,
            HistoricalAcquisitionEvidence(
                status=HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE,
                provider_id=request.provider_id,
                asset_class=request.asset_class,
                symbol=request.symbol,
                timeframe=request.timeframe,
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
            HistoricalAcquisitionEvidence(
                status=HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE,
                provider_id=request.provider_id,
                asset_class=request.asset_class,
                symbol=request.symbol,
                timeframe=request.timeframe,
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
    if ingestion.status is IngestionStatus.SUCCEEDED and ingestion.payload_uri:
        try:
            return _canonicalize_kraken(request, ingestion.payload_uri, ingestion.payload_sha256)
        except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
            return _retain_acquisition_evidence(
                request,
                HistoricalAcquisitionEvidence(
                    status=HistoricalAcquisitionStatus.FAILED,
                    provider_id=request.provider_id,
                    asset_class=request.asset_class,
                    symbol=request.symbol,
                    timeframe=request.timeframe,
                    admission_status=ingestion.admission_status,
                    raw_payload_uri=ingestion.payload_uri,
                    raw_payload_sha256=ingestion.payload_sha256,
                    source_attribution="Kraken public spot OHLC",
                    rationale="Kraken payload could not be normalized into canonical OHLCV.",
                    findings=("canonical-normalization-failed", str(exc)[:160]),
                ),
            )

    status = {
        IngestionStatus.POLICY_BLOCKED: HistoricalAcquisitionStatus.POLICY_BLOCKED,
        IngestionStatus.PROVIDER_UNAVAILABLE: HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE,
        IngestionStatus.FAILED: HistoricalAcquisitionStatus.FAILED,
    }[ingestion.status]
    return _retain_acquisition_evidence(
        request,
        HistoricalAcquisitionEvidence(
            status=status,
            provider_id=request.provider_id,
            asset_class=request.asset_class,
            symbol=request.symbol,
            timeframe=request.timeframe,
            admission_status=ingestion.admission_status,
            raw_payload_uri=ingestion.payload_uri,
            raw_payload_sha256=ingestion.payload_sha256,
            source_attribution="Kraken public spot OHLC",
            rationale=ingestion.rationale,
            findings=ingestion.findings,
        ),
    )


def _canonicalize_kraken(
    request: HistoricalAcquisitionRequest,
    payload_uri: str,
    payload_sha256: str | None,
) -> HistoricalAcquisitionEvidence:
    raw_payload = json.loads(_file_uri_path(payload_uri).read_text(encoding="utf-8"))
    errors = raw_payload.get("error")
    if errors:
        raise ValueError(f"Kraken returned errors: {errors}")
    result = raw_payload["result"]
    pair_keys = [key for key in result if key != "last"]
    if len(pair_keys) != 1:
        raise ValueError("Kraken response must contain exactly one OHLC pair")
    provider_rows = result[pair_keys[0]]
    if not isinstance(provider_rows, list) or len(provider_rows) < 2:
        raise ValueError("Kraken response requires one completed bar plus the live bar")

    completed_rows = provider_rows[:-1]
    source_path = _write_normalized_csv(request, completed_rows)
    imported = import_local_ohlcv(
        LocalOHLCVImportRequest(
            input_path=str(source_path),
            storage_root=request.storage_root,
            symbol=request.symbol,
            timeframe=_TIMEFRAMES[request.timeframe],
            source_uri="https://api.kraken.com/0/public/OHLC",
            calendar_assumption="kraken-continuous-market-completed-bars",
        )
    )
    return _retain_acquisition_evidence(
        request,
        HistoricalAcquisitionEvidence(
            status=HistoricalAcquisitionStatus.SUCCEEDED,
            provider_id=request.provider_id,
            asset_class=request.asset_class,
            symbol=request.symbol,
            timeframe=request.timeframe,
            admission_status=AdmissionStatus.APPROVED,
            raw_payload_uri=payload_uri,
            raw_payload_sha256=payload_sha256,
            dataset_revision_id=imported.dataset_revision_id,
            canonical_payload_uri=imported.payload_uri,
            canonical_metadata_uri=imported.metadata_uri,
            canonical_row_count=imported.row_count,
            source_attribution="Kraken public spot OHLC",
            rationale=(
                "Kraken completed bars were normalized through the canonical local "
                "OHLCV import path and retained as a dataset revision."
            ),
            findings=(
                "internal-use-only",
                "redistribution-disabled",
                "current-uncommitted-bar-excluded",
            ),
        ),
    )


def _write_normalized_csv(
    request: HistoricalAcquisitionRequest,
    rows: list[Any],
) -> Path:
    root = Path(request.storage_root).resolve() / "historical-acquisition" / "normalized"
    root.mkdir(parents=True, exist_ok=True)
    symbol = request.symbol.replace("/", "_")
    path = root / f"kraken-{symbol}-{request.timeframe}.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume"])
        for row in rows:
            if not isinstance(row, list) or len(row) < 7:
                raise ValueError("Kraken OHLC row has an unsupported shape")
            timestamp = datetime.fromtimestamp(int(row[0]), tz=UTC).isoformat()
            writer.writerow([timestamp, row[1], row[2], row[3], row[4], row[6]])
    return path


def _file_uri_path(uri: str) -> Path:
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        raise ValueError("retained provider payload must use a file URI")
    return Path(unquote(parsed.path))


def _retain_acquisition_evidence(
    request: HistoricalAcquisitionRequest,
    evidence: HistoricalAcquisitionEvidence,
) -> HistoricalAcquisitionEvidence:
    root = Path(request.storage_root).resolve() / "historical-acquisition"
    root.mkdir(parents=True, exist_ok=True)
    symbol = request.symbol.replace("/", "_")
    stem = (
        f"{request.provider_id.value}-{request.asset_class.value}-"
        f"{symbol}-{request.timeframe}"
    )
    path = root / f"{stem}.json"
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
