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
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.service import DesktopServiceError
from osca.desktop_api.workbench_data import resolve_governed_dataset
from osca.desktop_api.workbench_export import prepare_export
from osca.desktop_api.workbench_views import (
    create_view,
    delete_view,
    get_view,
    list_views,
    rename_view,
    update_view,
)


class D5DesktopApplicationService(D4DesktopApplicationService):
    """Extend D4 with narrow Python-authoritative workbench methods."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._handlers.update(
            {
                "workbench.series.get": self._workbench_series_get,
                "workbench.export.prepare": self._workbench_export_prepare,
                "workbench.view.list": self._workbench_view_list,
                "workbench.view.get": self._workbench_view_get,
                "workbench.view.create": self._workbench_view_create,
                "workbench.view.update": self._workbench_view_update,
                "workbench.view.rename": self._workbench_view_rename,
                "workbench.view.delete": self._workbench_view_delete,
            }
        )

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
        request = _chart_request(params, dataset)
        try:
            result = build_chart_series(request)
        except ValidationError as exc:
            raise DesktopServiceError("invalid_parameters", _validation_message(exc)) from exc
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

    def _workbench_export_prepare(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "asset_id",
                "timeframe",
                "start",
                "end",
                "max_rows",
                "derived",
            },
            "workbench.export.prepare",
        )
        profile_root = _required_path(params, "profile_root")
        asset_id = _required_text(params, "asset_id")
        dataset = resolve_governed_dataset(
            profile_root,
            asset_id=asset_id,
            timeframe=_required_text(params, "timeframe"),
        )
        request = _chart_request(params, dataset)
        display_downsampling_active = dataset.row_count is not None and dataset.row_count > request.max_rows
        with ProfileMutationLock(profile_root):
            return prepare_export(
                profile_root,
                asset_id=asset_id,
                dataset=dataset,
                request=request,
                display_downsampling_active=display_downsampling_active,
            )

    def _workbench_view_list(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root"}, "workbench.view.list")
        return list_views(_required_path(params, "profile_root"))

    def _workbench_view_get(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "view_id"}, "workbench.view.get")
        return get_view(
            _required_path(params, "profile_root"),
            _required_int(params, "view_id"),
        )

    def _workbench_view_create(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "name", "description", "config"},
            "workbench.view.create",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return create_view(
                profile_root,
                name=_required_text(params, "name"),
                description=_optional_text(params, "description"),
                config=_required_object(params, "config"),
            )

    def _workbench_view_update(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "view_id", "description", "config"},
            "workbench.view.update",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return update_view(
                profile_root,
                view_id=_required_int(params, "view_id"),
                description=_optional_text(params, "description"),
                config=_required_object(params, "config"),
            )

    def _workbench_view_rename(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "view_id", "name"},
            "workbench.view.rename",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return rename_view(
                profile_root,
                view_id=_required_int(params, "view_id"),
                name=_required_text(params, "name"),
            )

    def _workbench_view_delete(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "view_id"}, "workbench.view.delete")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return delete_view(profile_root, _required_int(params, "view_id"))


def _chart_request(params: dict[str, Any], dataset: Any) -> ChartSeriesRequest:
    try:
        return ChartSeriesRequest(
            dataset_revision_id=dataset.dataset_revision_id,
            payload_path=dataset.payload_path,
            symbol=dataset.symbol,
            timeframe=dataset.timeframe,
            start=_optional_datetime(params, "start"),
            end=_optional_datetime(params, "end"),
            max_rows=_optional_int(params, "max_rows", 2000),
            derived=_derived_requests(params),
        )
    except ValidationError as exc:
        raise DesktopServiceError("invalid_parameters", _validation_message(exc)) from exc


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


def _optional_text(params: dict[str, Any], name: str) -> str | None:
    if name not in params or params[name] is None:
        return None
    return _required_text(params, name)


def _required_path(params: dict[str, Any], name: str) -> Path:
    path = Path(_required_text(params, name)).expanduser()
    if not path.is_absolute():
        raise DesktopServiceError("invalid_parameters", f"{name} must be an absolute path")
    return path.resolve()


def _required_int(params: dict[str, Any], name: str) -> int:
    value = params.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise DesktopServiceError("invalid_parameters", f"{name} must be a positive integer")
    return value


def _optional_int(params: dict[str, Any], name: str, default: int) -> int:
    if name not in params or params[name] is None:
        return default
    value = params[name]
    if not isinstance(value, int) or isinstance(value, bool):
        raise DesktopServiceError("invalid_parameters", f"{name} must be an integer")
    return value


def _required_object(params: dict[str, Any], name: str) -> dict[str, Any]:
    value = params.get(name)
    if not isinstance(value, dict):
        raise DesktopServiceError("invalid_parameters", f"{name} must be an object")
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
