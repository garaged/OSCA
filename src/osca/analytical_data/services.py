from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable
from datetime import datetime
from itertools import pairwise
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from osca.analytical_data.contracts import (
    ChartRow,
    ChartSeriesRequest,
    ChartSeriesResult,
    DerivedSeriesEvidence,
    DerivedSeriesKind,
    DerivedSeriesRequest,
    DownsamplingMethod,
)

_REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


def build_chart_series(request: ChartSeriesRequest) -> ChartSeriesResult:
    payload_path = request.payload_path
    if not payload_path.is_file():
        raise FileNotFoundError(f"analytical payload does not exist: {payload_path}")

    table = pq.read_table(payload_path)
    missing = tuple(column for column in _REQUIRED_COLUMNS if column not in table.column_names)
    if missing:
        raise ValueError(f"analytical payload is missing required columns: {', '.join(missing)}")

    raw_rows: Any = table.select(list(_REQUIRED_COLUMNS)).to_pylist()
    if not isinstance(raw_rows, list) or not raw_rows:
        raise ValueError("analytical payload must contain at least one OHLCV row")

    source_rows = tuple(_normalize_row(row) for row in raw_rows)
    _validate_monotonic(source_rows)
    filtered_rows = tuple(
        row
        for row in source_rows
        if (request.start is None or row.timestamp >= request.start)
        and (request.end is None or row.timestamp <= request.end)
    )
    if not filtered_rows:
        raise ValueError("analytical query produced no rows")

    input_digest = _rows_digest(filtered_rows)
    derived_values: dict[str, tuple[float | None, ...]] = {}
    evidence: list[DerivedSeriesEvidence] = []
    for definition in request.derived:
        series_id = _series_id(definition)
        values = _derive(definition, filtered_rows)
        derived_values[series_id] = values
        evidence.append(
            DerivedSeriesEvidence(
                series_id=series_id,
                kind=definition.kind,
                window=definition.window,
                warmup_rows=_warmup_rows(definition),
                point_in_time_safe=True,
                input_digest=input_digest,
                output_digest=_values_digest(values),
            )
        )

    enriched = tuple(
        row.model_copy(
            update={
                "derived": {
                    series_id: values[index]
                    for series_id, values in derived_values.items()
                }
            }
        )
        for index, row in enumerate(filtered_rows)
    )
    returned, method = _downsample(enriched, request.max_rows)
    return ChartSeriesResult(
        dataset_revision_id=request.dataset_revision_id,
        payload_path=str(payload_path),
        symbol=request.symbol,
        timeframe=request.timeframe,
        source_row_count=len(source_rows),
        filtered_row_count=len(filtered_rows),
        returned_row_count=len(returned),
        first_timestamp=returned[0].timestamp,
        last_timestamp=returned[-1].timestamp,
        downsampling_method=method,
        downsampling_preserves_first_last=True,
        rows=returned,
        derived_evidence=tuple(evidence),
        payload_sha256=_sha256_file(payload_path),
    )


def _normalize_row(row: Any) -> ChartRow:
    if not isinstance(row, dict):
        raise ValueError("analytical payload rows must be key-value records")
    timestamp = row.get("timestamp")
    if not isinstance(timestamp, datetime):
        raise ValueError("analytical payload timestamp must be a datetime")
    values = {name: _finite_float(row.get(name), name) for name in _REQUIRED_COLUMNS[1:]}
    if values["high"] < max(values["open"], values["close"], values["low"]):
        raise ValueError("OHLC high is inconsistent")
    if values["low"] > min(values["open"], values["close"], values["high"]):
        raise ValueError("OHLC low is inconsistent")
    if values["volume"] < 0:
        raise ValueError("volume must not be negative")
    return ChartRow(timestamp=timestamp, **values)


def _finite_float(value: Any, name: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"{name} must be finite")
    return parsed


def _validate_monotonic(rows: tuple[ChartRow, ...]) -> None:
    for previous, current in pairwise(rows):
        if current.timestamp <= previous.timestamp:
            raise ValueError("analytical payload timestamps must be strictly increasing")


def _series_id(definition: DerivedSeriesRequest) -> str:
    if definition.window is None:
        return definition.kind.value
    return f"{definition.kind.value}_{definition.window}"


def _warmup_rows(definition: DerivedSeriesRequest) -> int:
    if definition.kind in {DerivedSeriesKind.SIMPLE_RETURN, DerivedSeriesKind.LOG_RETURN}:
        return 1
    if definition.kind is DerivedSeriesKind.EMA:
        return 0
    assert definition.window is not None
    return definition.window - 1


def _derive(
    definition: DerivedSeriesRequest,
    rows: tuple[ChartRow, ...],
) -> tuple[float | None, ...]:
    closes = tuple(row.close for row in rows)
    volumes = tuple(row.volume for row in rows)
    if definition.kind is DerivedSeriesKind.SIMPLE_RETURN:
        return _returns(closes, logarithmic=False)
    if definition.kind is DerivedSeriesKind.LOG_RETURN:
        return _returns(closes, logarithmic=True)
    assert definition.window is not None
    if definition.kind is DerivedSeriesKind.SMA:
        return _rolling_mean(closes, definition.window)
    if definition.kind is DerivedSeriesKind.EMA:
        return _ema(closes, definition.window)
    if definition.kind is DerivedSeriesKind.ROLLING_VOLATILITY:
        return _rolling_std(_returns(closes, logarithmic=False), definition.window)
    return _rolling_mean(volumes, definition.window)


def _returns(values: tuple[float, ...], *, logarithmic: bool) -> tuple[float | None, ...]:
    result: list[float | None] = [None]
    for previous, current in pairwise(values):
        if previous <= 0 or (logarithmic and current <= 0):
            result.append(None)
        elif logarithmic:
            result.append(math.log(current / previous))
        else:
            result.append((current / previous) - 1.0)
    return tuple(result)


def _rolling_mean(values: tuple[float, ...], window: int) -> tuple[float | None, ...]:
    result: list[float | None] = []
    running = 0.0
    for index, value in enumerate(values):
        running += value
        if index >= window:
            running -= values[index - window]
        result.append(running / window if index + 1 >= window else None)
    return tuple(result)


def _ema(values: tuple[float, ...], window: int) -> tuple[float | None, ...]:
    alpha = 2.0 / (window + 1.0)
    result: list[float | None] = []
    current: float | None = None
    for value in values:
        current = value if current is None else alpha * value + (1.0 - alpha) * current
        result.append(current)
    return tuple(result)


def _rolling_std(values: tuple[float | None, ...], window: int) -> tuple[float | None, ...]:
    result: list[float | None] = []
    for index in range(len(values)):
        segment = values[max(0, index - window + 1) : index + 1]
        if len(segment) < window or any(value is None for value in segment):
            result.append(None)
            continue
        numeric = tuple(float(value) for value in segment if value is not None)
        mean = sum(numeric) / window
        variance = sum((value - mean) ** 2 for value in numeric) / window
        result.append(math.sqrt(variance))
    return tuple(result)


def _downsample(
    rows: tuple[ChartRow, ...],
    max_rows: int,
) -> tuple[tuple[ChartRow, ...], DownsamplingMethod]:
    if len(rows) <= max_rows:
        return rows, DownsamplingMethod.NONE
    last = len(rows) - 1
    indexes = tuple(round(position * last / (max_rows - 1)) for position in range(max_rows))
    return tuple(rows[index] for index in indexes), DownsamplingMethod.EVENLY_SPACED


def _rows_digest(rows: Iterable[ChartRow]) -> str:
    payload = [row.model_dump(mode="json", exclude={"derived"}) for row in rows]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def _values_digest(values: tuple[float | None, ...]) -> str:
    return hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
