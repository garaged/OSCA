from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
from collections.abc import Iterable, Mapping
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

import pyarrow as pa
import pyarrow.parquet as pq

from osca.local_data_import.contracts import (
    LocalOHLCVBar,
    LocalOHLCVImportFormat,
    LocalOHLCVImportRequest,
    LocalOHLCVImportResult,
    LocalOHLCVQualityFinding,
    LocalOHLCVQualitySeverity,
)

_REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


def import_local_ohlcv(request: LocalOHLCVImportRequest) -> LocalOHLCVImportResult:
    input_path = Path(request.input_path)
    if not input_path.is_file():
        raise FileNotFoundError(f"local OHLCV input file does not exist: {input_path}")

    input_format = request.input_format or _infer_format(input_path)
    rows = _read_rows(input_path, input_format)
    bars = tuple(_bar_from_row(row, row_number=index) for index, row in enumerate(rows, start=1))
    if not bars:
        raise ValueError("local OHLCV input file must contain at least one data row")

    findings = _quality_findings(bars)
    error_findings = tuple(
        finding
        for finding in findings
        if finding.severity is LocalOHLCVQualitySeverity.ERROR
    )
    if error_findings:
        finding_ids = ", ".join(finding.finding_id for finding in error_findings)
        raise ValueError(f"local OHLCV quality validation failed: {finding_ids}")

    source_sha256 = _sha256_file(input_path)
    dataset_revision_id = _dataset_revision_id(
        source_sha256=source_sha256,
        symbol=request.symbol,
        timeframe=request.timeframe.value,
        input_format=input_format.value,
        revision_salt=request.revision_salt,
    )

    storage_root = Path(request.storage_root)
    payload_path = storage_root / "payloads" / f"{dataset_revision_id}.parquet"
    metadata_path = storage_root / "osca-local-data.sqlite"

    _write_payload(payload_path, bars)
    _write_metadata(
        metadata_path=metadata_path,
        dataset_revision_id=dataset_revision_id,
        request=request,
        input_format=input_format,
        source_sha256=source_sha256,
        payload_path=payload_path,
        bars=bars,
        findings=findings,
    )

    return LocalOHLCVImportResult(
        dataset_revision_id=dataset_revision_id,
        symbol=request.symbol,
        timeframe=request.timeframe,
        input_format=input_format,
        row_count=len(bars),
        first_timestamp=bars[0].timestamp,
        last_timestamp=bars[-1].timestamp,
        source_sha256=source_sha256,
        payload_uri=str(payload_path),
        metadata_uri=str(metadata_path),
        calendar_assumption=request.calendar_assumption,
        quality_findings=findings,
        deferred_boundaries=_deferred_boundaries(),
    )


def _infer_format(input_path: Path) -> LocalOHLCVImportFormat:
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        return LocalOHLCVImportFormat.CSV
    if suffix in {".parquet", ".pq"}:
        return LocalOHLCVImportFormat.PARQUET
    raise ValueError("local OHLCV input format must be csv or parquet")


def _read_rows(
    input_path: Path,
    input_format: LocalOHLCVImportFormat,
) -> tuple[Mapping[str, Any], ...]:
    if input_format is LocalOHLCVImportFormat.CSV:
        return _read_csv_rows(input_path)
    return _read_parquet_rows(input_path)


def _read_csv_rows(input_path: Path) -> tuple[Mapping[str, Any], ...]:
    with input_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        _require_columns(reader.fieldnames)
        return tuple(dict(row) for row in reader)


def _read_parquet_rows(input_path: Path) -> tuple[Mapping[str, Any], ...]:
    table = pq.read_table(input_path)
    _require_columns(table.column_names)
    raw_rows: Any = table.to_pylist()
    if not isinstance(raw_rows, list):
        raise ValueError("local OHLCV parquet input did not produce row records")
    return tuple(_ensure_mapping(row) for row in raw_rows)


def _ensure_mapping(row: Any) -> Mapping[str, Any]:
    if not isinstance(row, dict):
        raise ValueError("local OHLCV parquet rows must be key-value records")
    return row


def _require_columns(columns: Iterable[str] | None) -> None:
    if columns is None:
        raise ValueError("local OHLCV input file must include a header")
    column_set = set(columns)
    missing = tuple(column for column in _REQUIRED_COLUMNS if column not in column_set)
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"local OHLCV input file is missing required columns: {missing_list}")


def _bar_from_row(row: Mapping[str, Any], row_number: int) -> LocalOHLCVBar:
    try:
        return LocalOHLCVBar(
            timestamp=_parse_timestamp(row["timestamp"]),
            open=_parse_float(row["open"]),
            high=_parse_float(row["high"]),
            low=_parse_float(row["low"]),
            close=_parse_float(row["close"]),
            volume=_parse_float(row["volume"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid local OHLCV row {row_number}: {exc}") from exc


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO-8601 string or datetime")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_float(value: Any) -> float:
    if value is None:
        raise ValueError("numeric OHLCV values must be present")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("numeric OHLCV values must be finite")
    return parsed


def _quality_findings(
    bars: tuple[LocalOHLCVBar, ...],
) -> tuple[LocalOHLCVQualityFinding, ...]:
    findings: list[LocalOHLCVQualityFinding] = []
    previous_timestamp: datetime | None = None
    for index, bar in enumerate(bars, start=1):
        if previous_timestamp is not None and bar.timestamp <= previous_timestamp:
            finding_id = (
                "duplicate-timestamp"
                if bar.timestamp == previous_timestamp
                else "non-monotonic-timestamp"
            )
            findings.append(
                LocalOHLCVQualityFinding(
                    finding_id=finding_id,
                    severity=LocalOHLCVQualitySeverity.ERROR,
                    message="Local OHLCV timestamps must be strictly increasing.",
                    row_number=index,
                )
            )
        previous_timestamp = bar.timestamp
    return tuple(findings)


def _sha256_file(input_path: Path) -> str:
    digest = hashlib.sha256()
    with input_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dataset_revision_id(
    *,
    source_sha256: str,
    symbol: str,
    timeframe: str,
    input_format: str,
    revision_salt: str | None,
) -> UUID:
    salt = revision_salt or "content-only"
    return uuid5(
        NAMESPACE_URL,
        f"osca:local-ohlcv:{symbol}:{timeframe}:{input_format}:{source_sha256}:{salt}",
    )


def _write_payload(payload_path: Path, bars: tuple[LocalOHLCVBar, ...]) -> None:
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(
        [
            {
                "timestamp": bar.timestamp,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            for bar in bars
        ]
    )
    pq.write_table(table, payload_path)


def _write_metadata(
    *,
    metadata_path: Path,
    dataset_revision_id: UUID,
    request: LocalOHLCVImportRequest,
    input_format: LocalOHLCVImportFormat,
    source_sha256: str,
    payload_path: Path,
    bars: tuple[LocalOHLCVBar, ...],
    findings: tuple[LocalOHLCVQualityFinding, ...],
) -> None:
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(metadata_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS local_ohlcv_imports (
                dataset_revision_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                input_format TEXT NOT NULL,
                source_uri TEXT NOT NULL,
                source_path TEXT NOT NULL,
                source_sha256 TEXT NOT NULL,
                payload_uri TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                first_timestamp TEXT NOT NULL,
                last_timestamp TEXT NOT NULL,
                calendar_assumption TEXT NOT NULL,
                quality_findings_json TEXT NOT NULL,
                network_access_enabled INTEGER NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO local_ohlcv_imports (
                dataset_revision_id,
                symbol,
                timeframe,
                input_format,
                source_uri,
                source_path,
                source_sha256,
                payload_uri,
                row_count,
                first_timestamp,
                last_timestamp,
                calendar_assumption,
                quality_findings_json,
                network_access_enabled
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(dataset_revision_id),
                request.symbol,
                request.timeframe.value,
                input_format.value,
                request.source_uri,
                request.input_path,
                source_sha256,
                str(payload_path),
                len(bars),
                bars[0].timestamp.isoformat(),
                bars[-1].timestamp.isoformat(),
                request.calendar_assumption,
                json.dumps([finding.model_dump(mode="json") for finding in findings]),
                0,
            ),
        )


def _deferred_boundaries() -> dict[str, bool]:
    return {
        "live_provider_calls_enabled": False,
        "credential_materialization_enabled": False,
        "runtime_provider_routing_enabled": False,
        "production_ingestion_enabled": False,
        "real_capital_orders_enabled": False,
    }
