"""Governed profile-scoped dataset resolution for the D5 desktop workbench."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from osca.desktop_api.asset_catalog import ASSET_BY_ID, Asset
from osca.desktop_api.service import DesktopServiceError
from osca.historical_acquisition import (
    HistoricalAcquisitionEvidence,
    HistoricalAcquisitionStatus,
)
from osca.operator_experience import load_operator_config

_USABLE_ACQUISITION_STATUSES = {
    HistoricalAcquisitionStatus.SUCCEEDED,
    HistoricalAcquisitionStatus.FRESH,
    HistoricalAcquisitionStatus.STALE,
    HistoricalAcquisitionStatus.PARTIAL,
}


@dataclass(frozen=True, slots=True)
class GovernedDataset:
    dataset_revision_id: UUID
    payload_path: Path
    symbol: str
    timeframe: str
    source_kind: str
    source_attribution: str
    row_count: int | None
    effective_end: datetime


def resolve_governed_dataset(
    profile_root: Path,
    *,
    asset_id: str,
    timeframe: str,
) -> GovernedDataset:
    """Resolve the newest eligible retained dataset without accepting a client path."""

    asset = ASSET_BY_ID.get(asset_id)
    if asset is None:
        raise DesktopServiceError(
            "asset_not_found",
            f"Unknown canonical asset: {asset_id}",
        )
    normalized_timeframe = timeframe.strip()
    if normalized_timeframe not in {"1m", "5m", "15m", "30m", "1h", "4h", "1d"}:
        raise DesktopServiceError(
            "invalid_parameters",
            "timeframe must be one of 1m, 5m, 15m, 30m, 1h, 4h, or 1d",
        )
    storage_root = Path(load_operator_config(profile_root).storage_root).expanduser().resolve()
    candidates = [
        *_local_import_candidates(storage_root, asset, normalized_timeframe),
        *_acquisition_candidates(storage_root, asset, normalized_timeframe),
    ]
    if not candidates:
        raise DesktopServiceError(
            "workbench_data_unavailable",
            "No governed retained dataset is available for this asset and timeframe.",
        )
    return max(candidates, key=_dataset_rank)


def _local_import_candidates(
    storage_root: Path,
    asset: Asset,
    timeframe: str,
) -> tuple[GovernedDataset, ...]:
    metadata_path = storage_root / "osca-local-data.sqlite"
    if not metadata_path.is_file():
        return ()
    symbols = _accepted_symbols(asset)
    placeholders = ",".join("?" for _ in symbols)
    query = f"""
        SELECT dataset_revision_id, symbol, timeframe, source_uri, payload_uri,
               row_count, last_timestamp
        FROM local_ohlcv_imports
        WHERE upper(symbol) IN ({placeholders}) AND timeframe = ?
        ORDER BY last_timestamp DESC, dataset_revision_id DESC
    """
    try:
        with sqlite3.connect(metadata_path) as connection:
            rows = connection.execute(query, (*symbols, timeframe)).fetchall()
    except sqlite3.Error as exc:
        raise DesktopServiceError(
            "workbench_metadata_invalid",
            "Local analytical metadata could not be read safely.",
        ) from exc

    candidates: list[GovernedDataset] = []
    for revision, symbol, stored_timeframe, source_uri, payload_uri, row_count, last_at in rows:
        try:
            payload_path = _safe_payload_path(storage_root, str(payload_uri))
            dataset_revision_id = UUID(str(revision))
            effective_end = _aware_datetime(str(last_at))
        except (ValueError, OSError):
            continue
        if not payload_path.is_file():
            continue
        candidates.append(
            GovernedDataset(
                dataset_revision_id=dataset_revision_id,
                payload_path=payload_path,
                symbol=str(symbol),
                timeframe=str(stored_timeframe),
                source_kind="local-import",
                source_attribution=str(source_uri),
                row_count=int(row_count),
                effective_end=effective_end,
            )
        )
    return tuple(candidates)


def _acquisition_candidates(
    storage_root: Path,
    asset: Asset,
    timeframe: str,
) -> tuple[GovernedDataset, ...]:
    evidence_root = storage_root / "historical-acquisition"
    if not evidence_root.is_dir():
        return ()
    accepted_symbols = set(_accepted_symbols(asset))
    candidates: list[GovernedDataset] = []
    for path in evidence_root.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            evidence = HistoricalAcquisitionEvidence.model_validate(payload)
        except (OSError, ValueError):
            continue
        if evidence.status not in _USABLE_ACQUISITION_STATUSES:
            continue
        if evidence.symbol.upper() not in accepted_symbols or evidence.timeframe != timeframe:
            continue
        if evidence.dataset_revision_id is None or evidence.canonical_payload_uri is None:
            continue
        try:
            payload_path = _safe_payload_path(storage_root, evidence.canonical_payload_uri)
            dataset_revision_id = UUID(evidence.dataset_revision_id)
        except (ValueError, OSError):
            continue
        if not payload_path.is_file():
            continue
        candidates.append(
            GovernedDataset(
                dataset_revision_id=dataset_revision_id,
                payload_path=payload_path,
                symbol=evidence.symbol,
                timeframe=evidence.timeframe,
                source_kind="historical-acquisition",
                source_attribution=evidence.source_attribution,
                row_count=evidence.canonical_row_count,
                effective_end=evidence.end_at or evidence.completed_at,
            )
        )
    return tuple(candidates)


def _accepted_symbols(asset: Asset) -> tuple[str, ...]:
    values = {asset.symbol.upper(), *(alias.upper() for alias in asset.aliases)}
    if asset.asset_id == "equity:XNAS:AAPL":
        values.add("AAPL-SYNTHETIC")
    return tuple(sorted(values))


def _safe_payload_path(storage_root: Path, payload_uri: str) -> Path:
    candidate = Path(payload_uri).expanduser().resolve()
    root = storage_root.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("retained payload path escapes configured storage root")
    return candidate


def _aware_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("retained dataset timestamp must be timezone-aware")
    return parsed.astimezone(UTC)


def _dataset_rank(dataset: GovernedDataset) -> tuple[float, int, str]:
    source_rank = 1 if dataset.source_kind == "local-import" else 0
    return dataset.effective_end.timestamp(), source_rank, str(dataset.dataset_revision_id)
