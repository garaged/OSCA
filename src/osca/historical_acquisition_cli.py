from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal

import typer

from osca.historical_acquisition import (
    HistoricalAcquisitionRequest,
    HistoricalAcquisitionStatus,
    HistoricalAssetClass,
    run_historical_acquisition,
)
from osca.production_ingestion.contracts import ProductionProvider

app = typer.Typer(help="Acquire governed no-cost historical OHLCV evidence.")


def _parse_iso8601(value: str | None, *, option: str) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise typer.BadParameter(
            "must be an ISO-8601 timestamp, for example 2024-08-01T00:00:00Z",
            param_hint=option,
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise typer.BadParameter(
            "must include a timezone offset or Z suffix",
            param_hint=option,
        )
    return parsed.astimezone(UTC)


@app.command("fetch")
def fetch_historical(
    symbol: str,
    asset_class: HistoricalAssetClass,
    provider: ProductionProvider,
    timeframe: Literal["1m", "5m", "15m", "30m", "1h", "4h", "1d"] = "1d",
    storage_root: Annotated[Path, typer.Option("--storage-root")] = Path(".osca"),
    network_access_enabled: Annotated[
        bool,
        typer.Option("--network-access-enabled"),
    ] = False,
    since: Annotated[int | None, typer.Option("--since")] = None,
    start_at: Annotated[str | None, typer.Option("--start-at")] = None,
    end_at: Annotated[str | None, typer.Option("--end-at")] = None,
    expected_pair_key: Annotated[
        str | None,
        typer.Option("--expected-pair-key"),
    ] = None,
    minimum_rows: Annotated[int, typer.Option("--minimum-rows")] = 1,
    require_complete_range: Annotated[
        bool,
        typer.Option("--require-complete-range"),
    ] = False,
    freshness_max_age_seconds: Annotated[
        int | None,
        typer.Option("--freshness-max-age-seconds"),
    ] = None,
    cancel_requested: Annotated[
        bool,
        typer.Option("--cancel-requested"),
    ] = False,
    parser_version: Annotated[
        str,
        typer.Option("--parser-version"),
    ] = "kraken-ohlc-v1",
    normalizer_version: Annotated[
        str,
        typer.Option("--normalizer-version"),
    ] = "canonical-ohlcv-v1",
) -> None:
    """Fetch governed Kraken OHLC or retain a blocked-source decision."""

    evidence = run_historical_acquisition(
        HistoricalAcquisitionRequest(
            provider_id=provider,
            asset_class=asset_class,
            symbol=symbol,
            timeframe=timeframe,
            storage_root=str(storage_root),
            network_access_enabled=network_access_enabled,
            since=since,
            start_at=_parse_iso8601(start_at, option="--start-at"),
            end_at=_parse_iso8601(end_at, option="--end-at"),
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
