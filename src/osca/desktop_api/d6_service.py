"""D6 research-project desktop application methods."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from osca.desktop_api.d5_service import D5DesktopApplicationService
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.projects import (
    add_note,
    add_pin,
    archive_project,
    clone_project,
    create_project,
    delete_project,
    get_project,
    get_workspace,
    list_projects,
    list_workspaces,
    prepare_project_export,
    remove_pin,
    restore_project,
    save_workspace,
    update_note,
    update_pin,
    update_project,
)
from osca.desktop_api.service import DesktopServiceError


class D6DesktopApplicationService(D5DesktopApplicationService):
    """Extend D5 with narrow project organization methods."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._handlers.update(
            {
                "project.create": self._project_create,
                "project.list": self._project_list,
                "project.get": self._project_get,
                "project.update": self._project_update,
                "project.archive": self._project_archive,
                "project.restore": self._project_restore,
                "project.clone": self._project_clone,
                "project.delete": self._project_delete,
                "project.pin.add": self._project_pin_add,
                "project.pin.update": self._project_pin_update,
                "project.pin.remove": self._project_pin_remove,
                "project.note.add": self._project_note_add,
                "project.note.update": self._project_note_update,
                "project.workspace.save": self._project_workspace_save,
                "project.workspace.list": self._project_workspace_list,
                "project.workspace.get": self._project_workspace_get,
                "project.export.prepare": self._project_export_prepare,
            }
        )

    def _project_create(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "name", "objective", "horizon"}, "project.create")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return create_project(
                profile_root,
                name=_required_text(params, "name"),
                objective=_required_text(params, "objective", limit=1000),
                horizon=_optional_text(params, "horizon", limit=200),
            )

    def _project_list(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "include_archived", "include_deleted"}, "project.list")
        return list_projects(
            _required_path(params, "profile_root"),
            include_archived=_optional_bool(params, "include_archived", False),
            include_deleted=_optional_bool(params, "include_deleted", False),
        )

    def _project_get(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "project_id"}, "project.get")
        return get_project(
            _required_path(params, "profile_root"),
            _required_int(params, "project_id"),
        )

    def _project_update(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "project_id", "name", "objective", "horizon"},
            "project.update",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return update_project(
                profile_root,
                project_id=_required_int(params, "project_id"),
                name=_optional_text(params, "name"),
                objective=_optional_text(params, "objective", limit=1000),
                horizon=_optional_text(params, "horizon", limit=200),
            )

    def _project_archive(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "project_id"}, "project.archive")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return archive_project(profile_root, _required_int(params, "project_id"))

    def _project_restore(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "project_id"}, "project.restore")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return restore_project(profile_root, _required_int(params, "project_id"))

    def _project_clone(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "project_id", "name"}, "project.clone")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return clone_project(
                profile_root,
                project_id=_required_int(params, "project_id"),
                name=_required_text(params, "name"),
            )

    def _project_delete(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "project_id"}, "project.delete")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return delete_project(profile_root, _required_int(params, "project_id"))

    def _project_pin_add(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "project_id", "pin_type", "source_id", "label", "metadata"},
            "project.pin.add",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return add_pin(
                profile_root,
                project_id=_required_int(params, "project_id"),
                pin_type=_required_text(params, "pin_type"),
                source_id=_required_text(params, "source_id", limit=512),
                label=_required_text(params, "label", limit=160),
                metadata=_optional_object(params, "metadata"),
            )

    def _project_pin_update(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "pin_id", "label", "degraded_status"},
            "project.pin.update",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return update_pin(
                profile_root,
                pin_id=_required_int(params, "pin_id"),
                label=_optional_text(params, "label", limit=160),
                degraded_status=_optional_text(params, "degraded_status", limit=20),
            )

    def _project_pin_remove(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "pin_id"}, "project.pin.remove")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return remove_pin(profile_root, _required_int(params, "pin_id"))

    def _project_note_add(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "project_id", "title", "body"}, "project.note.add")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return add_note(
                profile_root,
                project_id=_required_int(params, "project_id"),
                title=_optional_text(params, "title", limit=120),
                body=_required_text(params, "body", limit=10_000),
            )

    def _project_note_update(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "note_id", "title", "body"}, "project.note.update")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return update_note(
                profile_root,
                note_id=_required_int(params, "note_id"),
                title=_optional_text(params, "title", limit=120),
                body=_required_text(params, "body", limit=10_000),
            )

    def _project_workspace_save(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "project_id", "name", "config"},
            "project.workspace.save",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return save_workspace(
                profile_root,
                project_id=_required_int(params, "project_id"),
                name=_required_text(params, "name"),
                config=_required_object(params, "config"),
            )

    def _project_workspace_list(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "project_id"}, "project.workspace.list")
        return list_workspaces(
            _required_path(params, "profile_root"),
            _required_int(params, "project_id"),
        )

    def _project_workspace_get(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "workspace_id"}, "project.workspace.get")
        return get_workspace(
            _required_path(params, "profile_root"),
            _required_int(params, "workspace_id"),
        )

    def _project_export_prepare(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "project_id"}, "project.export.prepare")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return prepare_project_export(
                profile_root,
                _required_int(params, "project_id"),
            )


def _allowed(params: dict[str, Any], allowed: set[str], method: str) -> None:
    unexpected = sorted(set(params) - allowed)
    if unexpected:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{method} received unsupported parameters: {', '.join(unexpected)}",
        )


def _required_path(params: dict[str, Any], name: str) -> Path:
    path = Path(_required_text(params, name)).expanduser()
    if not path.is_absolute():
        raise DesktopServiceError("invalid_parameters", f"{name} must be an absolute path")
    return path.resolve()


def _required_text(params: dict[str, Any], name: str, *, limit: int = 256) -> str:
    value = params.get(name)
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{name} must be a non-empty string up to {limit} characters",
        )
    return value.strip()


def _optional_text(
    params: dict[str, Any],
    name: str,
    *,
    limit: int = 256,
) -> str | None:
    if name not in params or params[name] is None:
        return None
    return _required_text(params, name, limit=limit)


def _required_int(params: dict[str, Any], name: str) -> int:
    value = params.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise DesktopServiceError("invalid_parameters", f"{name} must be a positive integer")
    return value


def _optional_bool(params: dict[str, Any], name: str, default: bool) -> bool:
    if name not in params or params[name] is None:
        return default
    value = params[name]
    if not isinstance(value, bool):
        raise DesktopServiceError("invalid_parameters", f"{name} must be a boolean")
    return value


def _required_object(params: dict[str, Any], name: str) -> dict[str, Any]:
    value = params.get(name)
    if not isinstance(value, dict):
        raise DesktopServiceError("invalid_parameters", f"{name} must be an object")
    return value


def _optional_object(params: dict[str, Any], name: str) -> dict[str, Any]:
    if name not in params or params[name] is None:
        return {}
    return _required_object(params, name)
