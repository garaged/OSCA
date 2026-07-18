import hashlib
import os
import tempfile
from collections.abc import Sequence
from pathlib import Path, PurePosixPath

import pyarrow as pa  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]

from osca.market_data.api import CanonicalDailyBar

DAILY_BAR_SCHEMA = pa.schema(
    [
        pa.field("instrument_id", pa.string(), nullable=False),
        pa.field("interval", pa.string(), nullable=False),
        pa.field("effective_date", pa.date32(), nullable=False),
        pa.field("source_timestamp", pa.timestamp("us", tz="UTC"), nullable=False),
        pa.field("complete", pa.bool_(), nullable=False),
        pa.field("open", pa.decimal128(38, 18), nullable=False),
        pa.field("high", pa.decimal128(38, 18), nullable=False),
        pa.field("low", pa.decimal128(38, 18), nullable=False),
        pa.field("close", pa.decimal128(38, 18), nullable=False),
        pa.field("volume", pa.decimal128(38, 18), nullable=False),
        pa.field("currency", pa.string(), nullable=False),
        pa.field("volume_unit", pa.string(), nullable=False),
        pa.field("provider_id", pa.string(), nullable=False),
        pa.field("source_identity", pa.string(), nullable=False),
        pa.field("request_id", pa.string(), nullable=False),
        pa.field("normalization_revision", pa.string(), nullable=False),
    ],
    metadata={b"osca.contract": b"osca.market-data.daily-bar/1.0.0"},
)


def serialize_daily_bars(bars: Sequence[CanonicalDailyBar]) -> bytes:
    ordered = tuple(sorted(bars, key=lambda bar: bar.effective_date))
    if not ordered:
        raise ValueError("canonical Parquet objects cannot be empty")
    identities = tuple((bar.instrument_id, bar.effective_date) for bar in ordered)
    if len(identities) != len(set(identities)):
        raise ValueError("canonical Parquet objects require unique instrument/date rows")
    table = pa.Table.from_pylist(
        [
            {
                **bar.model_dump(),
                "instrument_id": str(bar.instrument_id),
                "request_id": str(bar.request_id),
            }
            for bar in ordered
        ],
        schema=DAILY_BAR_SCHEMA,
    )
    output = pa.BufferOutputStream()
    pq.write_table(
        table,
        output,
        compression="zstd",
        version="2.6",
        data_page_version="2.0",
        use_dictionary=False,
        write_statistics=True,
        row_group_size=max(1, min(len(ordered), 4096)),
    )
    payload = output.getvalue().to_pybytes()
    if not isinstance(payload, bytes):
        raise TypeError("PyArrow returned a non-bytes payload")
    return payload


def deserialize_daily_bars(payload: bytes) -> tuple[CanonicalDailyBar, ...]:
    table = pq.read_table(pa.BufferReader(payload))
    if not table.schema.equals(DAILY_BAR_SCHEMA, check_metadata=True):
        raise ValueError("Parquet schema is not osca.market-data.daily-bar/1.0.0")
    return tuple(CanonicalDailyBar.model_validate(row) for row in table.to_pylist())


def payload_digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


class ImmutablePayloadStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def publish(self, object_key: str, payload: bytes) -> Path:
        relative = PurePosixPath(object_key)
        if relative.is_absolute() or ".." in relative.parts or relative.suffix != ".parquet":
            raise ValueError("object_key must be a safe relative Parquet path")
        destination = self._root.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        resolved_parent = destination.parent.resolve()
        if not resolved_parent.is_relative_to(self._root):
            raise ValueError("object_key escapes the configured payload root")
        if destination.exists():
            if payload_digest(destination.read_bytes()) != payload_digest(payload):
                raise FileExistsError("immutable payload key already contains different bytes")
            return destination
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.name}.", suffix=".staging", dir=resolved_parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
            directory_descriptor = os.open(resolved_parent, os.O_RDONLY)
            try:
                os.fsync(directory_descriptor)
            finally:
                os.close(directory_descriptor)
        finally:
            temporary.unlink(missing_ok=True)
        return destination
