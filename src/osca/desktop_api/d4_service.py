"""D4 asset catalog and watchlist desktop application methods."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from osca.desktop_api.asset_catalog import (
    add_watchlist_asset,
    create_watchlist,
    delete_watchlist,
    get_asset,
    list_recent,
    list_watchlists,
    record_recent,
    remove_watchlist_asset,
    rename_watchlist,
    search_assets,
)
from osca.desktop_api.d3_evidence_service import D3EvidenceApplicationService
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.service import DesktopServiceError
from osca.desktop_api.watchlist_order import reorder_watchlist


class D4DesktopApplicationService(D3EvidenceApplicationService):
    """Extend D3 with canonical offline markets and watchlist behavior."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._handlers.update(
            {
                "asset.search": self._asset_search,
                "asset.get": self._asset_get,
                "watchlist.list": self._watchlist_list,
                "watchlist.create": self._watchlist_create,
                "watchlist.rename": self._watchlist_rename,
                "watchlist.delete": self._watchlist_delete,
                "watchlist.asset.add": self._watchlist_asset_add,
                "watchlist.asset.remove": self._watchlist_asset_remove,
                "watchlist.reorder": self._watchlist_reorder,
                "asset.recent.list": self._recent_list,
                "asset.recent.record": self._recent_record,
            }
        )

    def _asset_search(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"query", "asset_class", "venue", "limit", "offset", "profile_root"}, "asset.search")
        return search_assets(
            _optional_search_query(params),
            asset_class=_optional_text(params, "asset_class"),
            venue=_optional_text(params, "venue"),
            limit=_optional_int(params, "limit", 50),
            offset=_optional_int(params, "offset", 0),
            profile_root=_optional_path(params, "profile_root"),
        )

    def _asset_get(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"asset_id", "profile_root"}, "asset.get")
        return get_asset(_required_text(params, "asset_id"), _optional_path(params, "profile_root"))

    def _watchlist_list(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root"}, "watchlist.list")
        return list_watchlists(_required_path(params, "profile_root"))

    def _watchlist_create(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "name"}, "watchlist.create")
        root = _required_path(params, "profile_root")
        with ProfileMutationLock(root):
            return create_watchlist(root, _required_text(params, "name"))

    def _watchlist_rename(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "watchlist_id", "name"}, "watchlist.rename")
        root = _required_path(params, "profile_root")
        with ProfileMutationLock(root):
            return rename_watchlist(root, _required_int(params, "watchlist_id"), _required_text(params, "name"))

    def _watchlist_delete(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "watchlist_id"}, "watchlist.delete")
        root = _required_path(params, "profile_root")
        with ProfileMutationLock(root):
            return delete_watchlist(root, _required_int(params, "watchlist_id"))

    def _watchlist_asset_add(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "watchlist_id", "asset_id"}, "watchlist.asset.add")
        root = _required_path(params, "profile_root")
        with ProfileMutationLock(root):
            return add_watchlist_asset(root, _required_int(params, "watchlist_id"), _required_text(params, "asset_id"))

    def _watchlist_asset_remove(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "watchlist_id", "asset_id"}, "watchlist.asset.remove")
        root = _required_path(params, "profile_root")
        with ProfileMutationLock(root):
            return remove_watchlist_asset(root, _required_int(params, "watchlist_id"), _required_text(params, "asset_id"))

    def _watchlist_reorder(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "watchlist_id", "asset_ids"}, "watchlist.reorder")
        values = params.get("asset_ids")
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            raise DesktopServiceError("invalid_parameters", "asset_ids must be an array of strings")
        root = _required_path(params, "profile_root")
        with ProfileMutationLock(root):
            return reorder_watchlist(root, _required_int(params, "watchlist_id"), values)

    def _recent_list(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "limit"}, "asset.recent.list")
        return list_recent(_required_path(params, "profile_root"), _optional_int(params, "limit", 10))

    def _recent_record(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "asset_id"}, "asset.recent.record")
        root = _required_path(params, "profile_root")
        with ProfileMutationLock(root):
            return record_recent(root, _required_text(params, "asset_id"))


def _allowed(params: dict[str, Any], allowed: set[str], method: str) -> None:
    unexpected = sorted(set(params) - allowed)
    if unexpected:
        raise DesktopServiceError("invalid_parameters", f"{method} received unsupported parameters: {', '.join(unexpected)}")


def _required_text(params: dict[str, Any], name: str) -> str:
    value = params.get(name)
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise DesktopServiceError("invalid_parameters", f"{name} must be a non-empty string up to 256 characters")
    return value.strip()


def _optional_text(params: dict[str, Any], name: str) -> str | None:
    if name not in params or params[name] is None:
        return None
    return _required_text(params, name)


def _optional_search_query(params: dict[str, Any]) -> str:
    if "query" not in params or params["query"] is None:
        return ""
    value = params["query"]
    if not isinstance(value, str) or len(value) > 256:
        raise DesktopServiceError("invalid_parameters", "query must be a string up to 256 characters")
    return value.strip()


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


def _required_path(params: dict[str, Any], name: str) -> Path:
    value = _required_text(params, name)
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise DesktopServiceError("invalid_parameters", f"{name} must be an absolute path")
    return path.resolve()


def _optional_path(params: dict[str, Any], name: str) -> Path | None:
    if name not in params or params[name] is None:
        return None
    return _required_path(params, name)
