"""D5 charting and quantitative-workbench desktop application methods."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from osca.analytical_data import (
    ChartSeriesRequest,
    DerivedSeriesKind,
    DerivedSeriesRequest,
    build_chart_series,
)
from osca.desktop_api.d4_service import D4DesktopApplicationService
from osca.desktop_api.service import DesktopServiceError
from osca.desktop_api.workbench_data import resolve_governed_dataset


class D5DesktopApplicationService(D4DesktopApplicationService):
    """Extend D4 with a narrow Python-authoritative chart-series boundary."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._handlers.update({"workbench.series.get": self._workbench_series_get})

    def _workbench_series_get(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "asset_id", "timeframe", "start", "end", "max_rows", "derived"},
            "workbench.series.get",
        )
        profile_root = _required_path(params, "profile_root")
        asset_id = _required_text(params, "asset_id")
        timeframe = _required_text(params, "timeframe")
        dataset = resolve_governed_dataset(
            profile_root,
            asset_id=asset_id,
            timeframe=timeframe,
        )
        try:
            request = ChartSeriesRequest(
                dataset_revision_id=dataset.dataset_revision_id,
                payload_path=dataset.payload_path,
                symbol=dataset.symbol,
                timeframe=dataset.timeframe,
                start=_optional_datetime(params, "start"),
                end=_optional_datetime(params, "end"),
                max_rows=_optional_int(params, "max_rows", 2000),
                derived=_derived_requests(params),
            )
            result = build_chart_series(request)
        except ValidationError as exc:
            raise DesktopServiceError(
                "invalid_parameters",
                _validation_message(exc),
            ) from exc
        payload = result.model_dump(mode="json", exclude={"payload_path"})
        return {
            "family": "osca.desktop-workbench-series.result",
            "version": "1.0.0",
            "asset_id": asset_id,
            "dataset": {
                "dataset_revision_id": str(dataset.dataset_revision_id),
                "symbol": dataset.symbol,
                "timeframe": dataset.timeframe,
                "source_kind": dataset.source_kind,
                "source_attribution": dataset.source_attribution,
                "retained_row_count": dataset.row_count,
                "effective_end": dataset.effective_end.isoformat(),
            },
            "series": payload,
            "network_access_enabled": False,
            "recommendations_enabled": False,
            "broker_connections_enabled": False,
            "real_capital_execution_enabled": False,
        }


def _derived_requests(params: dict[str, Any]) -> tuple[DerivedSeriesRequest, ...]:
    raw = params.get("derived", [])
    if not isinstance(raw, list):
        raise DesktopServiceError("invalid_parameters", "derived must be an array")
    definitions: list[DerivedSeriesRequest] = []
    for item in raw:
        if not isinstance(item, dict) or set(item) - {"kind", "window"}:
            raise DesktopServiceError(
                "invalid_parameters",
                "Each derived series must contain only kind and optional window.",
            )
        kind = item.get("kind")
        if not isinstance(kind, str):
            raise DesktopServiceError("invalid_parameters", "derived kind must be a string")
        try:
            definition = DerivedSeriesRequest(
                kind=DerivedSeriesKind(kind),
                window=item.get("window"),
            )
        except (ValueError, ValidationError) as exc:
            raise DesktopServiceError(
                "invalid_parameters",
                f"Invalid derived series definition: {kind}",
            ) from exc
        definitions.append(definition)
    return tuple(definitions)


def _allowed(params: dict[str, Any], allowed: set[str], method: str) -> None:
    unexpected = sorted(set(params) - allowed)
    if unexpected:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{method} received unsupported parameters: {', '.join(unexpected)}",
        )


def _required_text(params: dict[str, Any], name: str) -> str:
    value = params.get(name)
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{name} must be a non-empty string up to 256 characters",
        )
    return value.strip()


def _required_path(params: dict[str, Any], name: str) -> Path:
    path = Path(_required_text(params, name)).expanduser()
    if not path.is_absolute():
        raise DesktopServiceError("invalid_parameters", f"{name} must be an absolute path")
    return path.resolve()


def _optional_int(params: dict[str, Any], name: str, default: int) -> int:
    if name not in params or params[name] is None:
        return default
    value = params[name]
    if not isinstance(value, int) or isinstance(value, bool):
        raise DesktopServiceError("invalid_parameters", f"{name} must be an integer")
    return value


def _optional_datetime(params: dict[str, Any], name: str) -> datetime | None:
    if name not in params or params[name] is None:
        return None
    value = params[name]
    if not isinstance(value, str) or len(value) > 80:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{name} must be an ISO-8601 timestamp string",
        )
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{name} must be an ISO-8601 timestamp string",
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{name} must include timezone information",
        )
    return parsed


def _validation_message(exc: ValidationError) -> str:
    first = exc.errors()[0]
    location = ".".join(str(part) for part in first.get("loc", ())) or "request"
    return f"Invalid workbench request at {location}: {first.get('msg', 'validation failed')}"
