from collections import defaultdict
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from osca.market_data.api import DatasetLayer, DatasetManifest


class UsageSummary(BaseModel):
    model_config = ConfigDict(frozen=True)
    layer: DatasetLayer
    provider_id: str
    instrument_id: UUID
    object_count: int = Field(ge=0)
    row_count: int = Field(ge=0)
    byte_size: int = Field(ge=0)
    protected_bytes: int = Field(ge=0)


class StorageInspection(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.cache.storage-inspection"] = "osca.cache.storage-inspection"
    version: Literal["1.0.0"] = "1.0.0"
    usage: tuple[UsageSummary, ...]
    manifests: tuple[DatasetManifest, ...]


def inspect_storage(manifests: tuple[DatasetManifest, ...]) -> StorageInspection:
    totals: dict[tuple[DatasetLayer, str, UUID], list[int]] = defaultdict(
        lambda: [0, 0, 0, 0]
    )
    for manifest in manifests:
        key = (manifest.layer, manifest.provider_id, manifest.instrument_id)
        values = totals[key]
        values[0] += 1
        values[1] += manifest.row_count
        values[2] += manifest.byte_size
        if manifest.protected or manifest.layer is DatasetLayer.CANONICAL:
            values[3] += manifest.byte_size
    usage = tuple(
        UsageSummary(
            layer=key[0],
            provider_id=key[1],
            instrument_id=key[2],
            object_count=values[0],
            row_count=values[1],
            byte_size=values[2],
            protected_bytes=values[3],
        )
        for key, values in sorted(
            totals.items(), key=lambda item: (item[0][0], item[0][1], str(item[0][2]))
        )
    )
    ordered = tuple(sorted(manifests, key=lambda item: (item.created_at, str(item.manifest_id))))
    return StorageInspection(usage=usage, manifests=ordered)
