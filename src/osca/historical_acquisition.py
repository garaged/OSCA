from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import urlencode

import typer
from pydantic import BaseModel, ConfigDict, Field

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
    payload_uri: str | None = None
    payload_sha256: str | None = None
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
    status = {
        IngestionStatus.SUCCEEDED: HistoricalAcquisitionStatus.SUCCEEDED,
        IngestionStatus.POLICY_BLOCKED: HistoricalAcquisitionStatus.POLICY_BLOCKED,
        IngestionStatus.PROVIDER_UNAVAILABLE: HistoricalAcquisitionStatus.PROVIDER_UNAVAILABLE,
        IngestionStatus.FAILED: HistoricalAcquisitionStatus.FAILED,
    }[ingestion.status]
    evidence = HistoricalAcquisitionEvidence(
        status=status,
        provider_id=request.provider_id,
        asset_class=request.asset_class,
        symbol=request.symbol,
        timeframe=request.timeframe,
        admission_status=ingestion.admission_status,
        payload_uri=ingestion.payload_uri,
        payload_sha256=ingestion.payload_sha256,
        source_attribution="Kraken public spot OHLC",
        rationale=ingestion.rationale,
        findings=ingestion.findings,
    )
    return _retain_acquisition_evidence(request, evidence)


def _retain_acquisition_evidence(
    request: HistoricalAcquisitionRequest,
    evidence: HistoricalAcquisitionEvidence,
) -> HistoricalAcquisitionEvidence:
    root = Path(request.storage_root).resolve() / "historical-acquisition"
    root.mkdir(parents=True, exist_ok=True)
    stem = f"{request.provider_id.value}-{request.asset_class.value}-{request.symbol.replace('/', '_')}-{request.timeframe}"
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
