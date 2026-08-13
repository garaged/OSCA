"""Full-resolution CSV and reproduction-metadata export for D5."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from osca.analytical_data import ChartSeriesRequest, build_full_resolution_chart_series
from osca.desktop_api.service import DesktopServiceError
from osca.desktop_api.workbench_data import GovernedDataset


def prepare_export(
    profile_root: Path,
    *,
    asset_id: str,
    dataset: GovernedDataset,
    request: ChartSeriesRequest,
    display_downsampling_active: bool,
) -> dict[str, Any]:
    """Write a full-resolution evidence export beneath the selected profile."""

    try:
        result = build_full_resolution_chart_series(request)
    except (OSError, ValueError) as exc:
        raise DesktopServiceError(
            "workbench_export_failed",
            f"Full-resolution export could not be prepared: {exc}",
        ) from exc

    export_id = uuid4()
    export_root = profile_root / ".osca" / "exports" / "workbench" / str(export_id)
    export_root.mkdir(parents=True, exist_ok=False)
    csv_path = export_root / "series.csv"
    metadata_path = export_root / "metadata.json"
    derived_ids = [evidence.series_id for evidence in result.derived_evidence]

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "open", "high", "low", "close", "volume", *derived_ids])
        for row in result.rows:
            writer.writerow(
                [
                    row.timestamp.isoformat(),
                    row.open,
                    row.high,
                    row.low,
                    row.close,
                    row.volume,
                    *(row.derived.get(series_id) for series_id in derived_ids),
                ]
            )

    metadata = {
        "family": "osca.workbench-export.metadata",
        "version": "1.0.0",
        "export_id": str(export_id),
        "created_at": datetime.now(UTC).isoformat(),
        "asset_id": asset_id,
        "dataset_revision_id": str(dataset.dataset_revision_id),
        "symbol": dataset.symbol,
        "timeframe": dataset.timeframe,
        "source_kind": dataset.source_kind,
        "source_attribution": dataset.source_attribution,
        "effective_range": {
            "first_timestamp": result.first_timestamp.isoformat(),
            "last_timestamp": result.last_timestamp.isoformat(),
        },
        "requested_series": [
            {"kind": item.kind.value, "window": item.window} for item in request.derived
        ],
        "payload_sha256": result.payload_sha256,
        "full_resolution_row_count": result.returned_row_count,
        "display_downsampling_was_active": display_downsampling_active,
        "display_rows_exported": False,
        "csv_sha256": _sha256(csv_path),
        "network_used": False,
        "recommendations_enabled": False,
        "broker_execution_enabled": False,
        "real_capital_enabled": False,
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "family": "osca.desktop-workbench-export.result",
        "version": "1.0.0",
        "export_id": str(export_id),
        "row_count": result.returned_row_count,
        "csv_path": str(csv_path),
        "metadata_path": str(metadata_path),
        "csv_sha256": metadata["csv_sha256"],
        "display_downsampling_was_active": display_downsampling_active,
        "full_resolution": True,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
