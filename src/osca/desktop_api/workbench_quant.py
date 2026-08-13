"""Bounded quantitative-analysis composition for the D5 desktop workbench."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from osca.desktop_api.asset_catalog import ASSET_BY_ID
from osca.desktop_api.service import DesktopServiceError
from osca.desktop_api.workbench_data import GovernedDataset, resolve_governed_dataset
from osca.quantitative_analysis import (
    DatasetComparisonRequest,
    QuantitativeAnalysisRequest,
    analyze_dataset,
    compare_datasets,
)


def get_quantitative_analysis(
    profile_root: Path,
    *,
    asset_id: str,
    timeframe: str,
    start: datetime | None,
    end: datetime | None,
    max_rows: int,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    dataset = resolve_governed_dataset(
        profile_root,
        asset_id=asset_id,
        timeframe=timeframe,
    )
    request = _analysis_request(
        dataset,
        start=start,
        end=end,
        parameters=parameters,
    )
    try:
        result = analyze_dataset(request)
    except ValueError as exc:
        raise DesktopServiceError(
            "invalid_parameters",
            f"Invalid quantitative request: {exc}",
        ) from exc
    point_payloads = [point.model_dump(mode="json") for point in result.points]
    displayed = _bounded(point_payloads, max_rows)
    return {
        "family": "osca.desktop-workbench-analysis.result",
        "version": "1.0.0",
        "asset_id": asset_id,
        "dataset_revision_id": str(dataset.dataset_revision_id),
        "symbol": dataset.symbol,
        "timeframe": dataset.timeframe,
        "source_attribution": dataset.source_attribution,
        "source_point_count": len(point_payloads),
        "displayed_point_count": len(displayed),
        "display_method": (
            "none" if len(displayed) == len(point_payloads) else "evenly_spaced"
        ),
        "display_preserves_first_last": True,
        "summary": result.summary.model_dump(mode="json"),
        "parameters": result.parameters,
        "assumptions": list(result.assumptions),
        "findings": list(result.findings),
        "input_digest": result.input_digest,
        "output_digest": result.output_digest,
        "point_in_time_safe": result.point_in_time_safe,
        "points": displayed,
        "network_access_enabled": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_execution_enabled": False,
    }


def get_comparison(
    profile_root: Path,
    *,
    primary_asset_id: str,
    comparison_asset_id: str,
    timeframe: str,
    start: datetime | None,
    end: datetime | None,
    rolling_window: int,
    max_rows: int,
) -> dict[str, Any]:
    primary_asset = ASSET_BY_ID.get(primary_asset_id)
    comparison_asset = ASSET_BY_ID.get(comparison_asset_id)
    if primary_asset is None or comparison_asset is None:
        raise DesktopServiceError(
            "asset_not_found",
            "Comparison requires known canonical assets.",
        )
    if (
        primary_asset.asset_class != comparison_asset.asset_class
        or primary_asset.currency != comparison_asset.currency
    ):
        raise DesktopServiceError(
            "workbench_comparison_incompatible",
            "Direct comparison requires matching asset-class and currency semantics.",
        )
    primary = resolve_governed_dataset(
        profile_root,
        asset_id=primary_asset_id,
        timeframe=timeframe,
    )
    comparison = resolve_governed_dataset(
        profile_root,
        asset_id=comparison_asset_id,
        timeframe=timeframe,
    )
    if primary.timeframe != comparison.timeframe:
        raise DesktopServiceError(
            "workbench_comparison_incompatible",
            "Direct comparison requires matching timeframes.",
        )
    try:
        result = compare_datasets(
            DatasetComparisonRequest(
                primary=_analysis_request(
                    primary,
                    start=start,
                    end=end,
                    parameters={},
                ),
                benchmark=_analysis_request(
                    comparison,
                    start=start,
                    end=end,
                    parameters={},
                ),
                rolling_window=rolling_window,
            )
        )
    except (ValidationError, ValueError) as exc:
        raise DesktopServiceError(
            "invalid_parameters",
            f"Invalid comparison request: {exc}",
        ) from exc
    points = [point.model_dump(mode="json") for point in result.points]
    displayed = _bounded(points, max_rows)
    return {
        "family": "osca.desktop-workbench-comparison.result",
        "version": "1.0.0",
        "primary": {
            "asset_id": primary_asset_id,
            "dataset_revision_id": str(primary.dataset_revision_id),
            "symbol": primary.symbol,
            "currency": primary_asset.currency,
            "timeframe": primary.timeframe,
            "source_attribution": primary.source_attribution,
        },
        "comparison": {
            "asset_id": comparison_asset_id,
            "dataset_revision_id": str(comparison.dataset_revision_id),
            "symbol": comparison.symbol,
            "currency": comparison_asset.currency,
            "timeframe": comparison.timeframe,
            "source_attribution": comparison.source_attribution,
        },
        "aligned_return_count": result.aligned_return_count,
        "correlation": result.correlation,
        "beta": result.beta,
        "rolling_window": rolling_window,
        "displayed_point_count": len(displayed),
        "display_method": (
            "none" if len(displayed) == len(points) else "evenly_spaced"
        ),
        "display_preserves_first_last": True,
        "points": displayed,
        "assumptions": list(result.assumptions),
        "input_digest": result.input_digest,
        "output_digest": result.output_digest,
        "point_in_time_safe": result.point_in_time_safe,
        "normalization_basis": (
            "close-to-close simple returns aligned on exact shared timestamps"
        ),
        "network_access_enabled": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_execution_enabled": False,
    }


def _analysis_request(
    dataset: GovernedDataset,
    *,
    start: datetime | None,
    end: datetime | None,
    parameters: dict[str, Any],
) -> QuantitativeAnalysisRequest:
    allowed = {
        "periods_per_year",
        "risk_free_rate",
        "confidence_level",
        "rsi_window",
        "atr_window",
        "bollinger_window",
        "bollinger_stddevs",
        "fast_window",
        "slow_window",
        "signal_window",
    }
    unexpected = sorted(set(parameters) - allowed)
    if unexpected:
        raise DesktopServiceError(
            "invalid_parameters",
            f"Unsupported quantitative parameters: {', '.join(unexpected)}",
        )
    try:
        return QuantitativeAnalysisRequest(
            dataset_revision_id=dataset.dataset_revision_id,
            payload_path=dataset.payload_path,
            symbol=dataset.symbol,
            timeframe=dataset.timeframe,
            start=start,
            end=end,
            **parameters,
        )
    except ValidationError as exc:
        raise DesktopServiceError(
            "invalid_parameters",
            f"Invalid quantitative parameters: {exc}",
        ) from exc


def _bounded(
    values: list[dict[str, Any]],
    max_rows: int,
) -> list[dict[str, Any]]:
    if max_rows < 2 or max_rows > 5000:
        raise DesktopServiceError(
            "invalid_parameters",
            "max_rows must be between 2 and 5000",
        )
    if len(values) <= max_rows:
        return values
    last = len(values) - 1
    indexes = [round(index * last / (max_rows - 1)) for index in range(max_rows)]
    return [values[index] for index in indexes]
