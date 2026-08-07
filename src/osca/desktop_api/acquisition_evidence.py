"""Profile-scoped retained acquisition evidence inspection for D3 desktop."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from osca.historical_acquisition import HistoricalAcquisitionEvidence


def list_retained_acquisitions(
    storage_root: Path,
    *,
    limit: int = 50,
) -> dict[str, Any]:
    """Read bounded canonical evidence files under one profile storage root."""

    root = storage_root.resolve() / "historical-acquisition"
    if not root.is_dir():
        return {
            "family": "osca.desktop-acquisition-list.result",
            "version": "1.0.0",
            "acquisitions": [],
            "invalid_evidence_count": 0,
        }
    candidates = sorted(
        root.glob("*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    acquisitions: list[dict[str, Any]] = []
    invalid = 0
    for path in candidates:
        try:
            evidence = HistoricalAcquisitionEvidence.model_validate_json(
                path.read_text(encoding="utf-8")
            )
        except (OSError, ValueError):
            invalid += 1
            continue
        acquisitions.append(evidence.model_dump(mode="json"))
        if len(acquisitions) >= limit:
            break
    return {
        "family": "osca.desktop-acquisition-list.result",
        "version": "1.0.0",
        "acquisitions": acquisitions,
        "invalid_evidence_count": invalid,
    }
