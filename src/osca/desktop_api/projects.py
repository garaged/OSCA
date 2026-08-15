"""Profile-scoped research projects for the D6 desktop surface."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

from osca.desktop_api.service import DesktopServiceError

_SCHEMA_VERSION = 1
_PROJECT_STATUSES = {"active", "archived", "deleted"}
_PIN_TYPES = {
    "asset",
    "watchlist",
    "dataset_revision",
    "local_import",
    "workbench_view",
    "workbench_export",
    "strategy",
    "strategy_version",
    "backtest_result",
    "report",
    "external_reference",
}


def create_project(
    profile_root: Path,
    *,
    name: str,
    objective: str,
    horizon: str | None = None,
) -> dict[str, Any]:
    normalized_name = _bounded_text(name, "Project name", limit=80)
    normalized_objective = _bounded_text(objective, "Project objective", limit=1000)
    normalized_horizon = _optional_bounded_text(horizon, "Project horizon", limit=200)
    project_uuid = str(uuid4())
    with _connect(profile_root) as connection:
        try:
            cursor = connection.execute(
                "INSERT INTO projects(project_uuid, name, objective, horizon) "
                "VALUES (?, ?, ?, ?)",
                (
                    project_uuid,
                    normalized_name,
                    normalized_objective,
                    normalized_horizon,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise DesktopServiceError(
                "project_conflict",
                "A research project with that name already exists.",
            ) from exc
        assert cursor.lastrowid is not None
        project_id = int(cursor.lastrowid)
        _append_event(
            connection,
            project_id,
            "project.created",
            {"name": normalized_name, "objective": normalized_objective},
        )
        return _single_project(connection, project_id)


def list_projects(
    profile_root: Path,
    *,
    include_archived: bool = False,
    include_deleted: bool = False,
) -> dict[str, Any]:
    statuses = ["active"]
    if include_archived:
        statuses.append("archived")
    if include_deleted:
        statuses.append("deleted")
    placeholders = ",".join("?" for _ in statuses)
    with _connect(profile_root) as connection:
        rows = connection.execute(
            "SELECT * FROM projects "
            f"WHERE status IN ({placeholders}) ORDER BY lower(name), id",
            tuple(statuses),
        ).fetchall()
        projects = [_project_summary(cast(sqlite3.Row, row)) for row in rows]
    return {
        "family": "osca.desktop-project-list.result",
        "version": "1.0.0",
        "schema_version": _SCHEMA_VERSION,
        "projects": projects,
    }


def get_project(profile_root: Path, project_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        _require_project(connection, project_id)
        return _single_project(connection, project_id)


def update_project(
    profile_root: Path,
    *,
    project_id: int,
    name: str | None = None,
    objective: str | None = None,
    horizon: str | None = None,
) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    if name is not None:
        updates["name"] = _bounded_text(name, "Project name", limit=80)
    if objective is not None:
        updates["objective"] = _bounded_text(
            objective,
            "Project objective",
            limit=1000,
        )
    if horizon is not None:
        updates["horizon"] = _optional_bounded_text(
            horizon,
            "Project horizon",
            limit=200,
        )
    if not updates:
        raise DesktopServiceError(
            "invalid_parameters",
            "At least one project field must be supplied.",
        )
    with _connect(profile_root) as connection:
        _require_mutable_project(connection, project_id)
        assignments = ", ".join(f"{key}=?" for key in updates)
        values = [*updates.values(), project_id]
        try:
            connection.execute(
                f"UPDATE projects SET {assignments}, "
                "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
                tuple(values),
            )
        except sqlite3.IntegrityError as exc:
            raise DesktopServiceError(
                "project_conflict",
                "A research project with that name already exists.",
            ) from exc
        _append_event(connection, project_id, "project.updated", updates)
        return _single_project(connection, project_id)


def archive_project(profile_root: Path, project_id: int) -> dict[str, Any]:
    return _transition_project(profile_root, project_id, "archived", "project.archived")


def restore_project(profile_root: Path, project_id: int) -> dict[str, Any]:
    return _transition_project(profile_root, project_id, "active", "project.restored")


def delete_project(profile_root: Path, project_id: int) -> dict[str, Any]:
    return _transition_project(profile_root, project_id, "deleted", "project.deleted")


def clone_project(profile_root: Path, *, project_id: int, name: str) -> dict[str, Any]:
    clone_name = _bounded_text(name, "Project name", limit=80)
    clone_uuid = str(uuid4())
    with _connect(profile_root) as connection:
        source = _require_project(connection, project_id)
        try:
            cursor = connection.execute(
                "INSERT INTO projects(project_uuid, name, objective, horizon, cloned_from_uuid) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    clone_uuid,
                    clone_name,
                    source["objective"],
                    source["horizon"],
                    source["project_uuid"],
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise DesktopServiceError(
                "project_conflict",
                "A research project with that name already exists.",
            ) from exc
        assert cursor.lastrowid is not None
        clone_id = int(cursor.lastrowid)
        for pin in connection.execute(
            "SELECT pin_type, source_id, label, metadata_json, degraded_status "
            "FROM project_pins WHERE project_id=? ORDER BY id",
            (project_id,),
        ):
            connection.execute(
                "INSERT INTO project_pins(project_id, pin_type, source_id, label, "
                "metadata_json, degraded_status) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    clone_id,
                    pin["pin_type"],
                    pin["source_id"],
                    pin["label"],
                    pin["metadata_json"],
                    pin["degraded_status"],
                ),
            )
        for note in connection.execute(
            "SELECT title, body FROM project_notes WHERE project_id=? ORDER BY id",
            (project_id,),
        ):
            connection.execute(
                "INSERT INTO project_notes(project_id, title, body) VALUES (?, ?, ?)",
                (clone_id, note["title"], note["body"]),
            )
        for workspace in connection.execute(
            "SELECT name, config_json FROM project_workspaces WHERE project_id=? ORDER BY id",
            (project_id,),
        ):
            connection.execute(
                "INSERT INTO project_workspaces(project_id, name, config_json) "
                "VALUES (?, ?, ?)",
                (clone_id, workspace["name"], workspace["config_json"]),
            )
        _append_event(
            connection,
            clone_id,
            "project.cloned",
            {"source_project_uuid": source["project_uuid"]},
        )
        _append_event(
            connection,
            project_id,
            "project.clone_created",
            {"clone_project_uuid": clone_uuid},
        )
        return _single_project(connection, clone_id)


def add_pin(
    profile_root: Path,
    *,
    project_id: int,
    pin_type: str,
    source_id: str,
    label: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_type = _pin_type(pin_type)
    normalized_source = _bounded_text(source_id, "Pin source identity", limit=512)
    normalized_label = _bounded_text(label, "Pin label", limit=160)
    normalized_metadata = _safe_json_object(metadata or {}, "Pin metadata", limit=8192)
    with _connect(profile_root) as connection:
        _require_mutable_project(connection, project_id)
        cursor = connection.execute(
            "INSERT INTO project_pins(project_id, pin_type, source_id, label, metadata_json) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                project_id,
                normalized_type,
                normalized_source,
                normalized_label,
                _json(normalized_metadata),
            ),
        )
        assert cursor.lastrowid is not None
        pin_id = int(cursor.lastrowid)
        _append_event(
            connection,
            project_id,
            "pin.added",
            {"pin_id": pin_id, "pin_type": normalized_type},
        )
        return _single_pin(connection, pin_id)


def update_pin(
    profile_root: Path,
    *,
    pin_id: int,
    label: str | None = None,
    degraded_status: str | None = None,
) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    if label is not None:
        updates["label"] = _bounded_text(label, "Pin label", limit=160)
    if degraded_status is not None:
        updates["degraded_status"] = _degraded_status(degraded_status)
    if not updates:
        raise DesktopServiceError(
            "invalid_parameters",
            "At least one pin field must be supplied.",
        )
    with _connect(profile_root) as connection:
        pin = _require_pin(connection, pin_id)
        _require_mutable_project(connection, int(pin["project_id"]))
        assignments = ", ".join(f"{key}=?" for key in updates)
        connection.execute(
            f"UPDATE project_pins SET {assignments}, "
            "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
            (*updates.values(), pin_id),
        )
        _append_event(
            connection,
            int(pin["project_id"]),
            "pin.updated",
            {"pin_id": pin_id, **updates},
        )
        return _single_pin(connection, pin_id)


def remove_pin(profile_root: Path, pin_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        pin = _require_pin(connection, pin_id)
        project_id = int(pin["project_id"])
        _require_mutable_project(connection, project_id)
        connection.execute("DELETE FROM project_pins WHERE id=?", (pin_id,))
        _append_event(connection, project_id, "pin.removed", {"pin_id": pin_id})
    return {
        "family": "osca.desktop-project-pin-delete.result",
        "version": "1.0.0",
        "deleted": True,
        "pin_id": pin_id,
    }


def add_note(
    profile_root: Path,
    *,
    project_id: int,
    title: str | None,
    body: str,
) -> dict[str, Any]:
    normalized_title = _optional_bounded_text(title, "Note title", limit=120)
    normalized_body = _bounded_text(body, "Note body", limit=10_000)
    with _connect(profile_root) as connection:
        _require_mutable_project(connection, project_id)
        cursor = connection.execute(
            "INSERT INTO project_notes(project_id, title, body) VALUES (?, ?, ?)",
            (project_id, normalized_title, normalized_body),
        )
        assert cursor.lastrowid is not None
        note_id = int(cursor.lastrowid)
        _append_event(connection, project_id, "note.added", {"note_id": note_id})
        return _single_note(connection, note_id)


def update_note(
    profile_root: Path,
    *,
    note_id: int,
    title: str | None,
    body: str,
) -> dict[str, Any]:
    normalized_title = _optional_bounded_text(title, "Note title", limit=120)
    normalized_body = _bounded_text(body, "Note body", limit=10_000)
    with _connect(profile_root) as connection:
        note = _require_note(connection, note_id)
        project_id = int(note["project_id"])
        _require_mutable_project(connection, project_id)
        connection.execute(
            "UPDATE project_notes SET title=?, body=?, "
            "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
            (normalized_title, normalized_body, note_id),
        )
        _append_event(connection, project_id, "note.updated", {"note_id": note_id})
        return _single_note(connection, note_id)


def save_workspace(
    profile_root: Path,
    *,
    project_id: int,
    name: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    normalized_name = _bounded_text(name, "Workspace name", limit=80)
    normalized_config = _safe_json_object(config, "Workspace configuration", limit=32_768)
    with _connect(profile_root) as connection:
        _require_mutable_project(connection, project_id)
        encoded = _json(normalized_config)
        row = connection.execute(
            "SELECT id FROM project_workspaces WHERE project_id=? AND lower(name)=lower(?)",
            (project_id, normalized_name),
        ).fetchone()
        if row is None:
            cursor = connection.execute(
                "INSERT INTO project_workspaces(project_id, name, config_json) "
                "VALUES (?, ?, ?)",
                (project_id, normalized_name, encoded),
            )
            assert cursor.lastrowid is not None
            workspace_id = int(cursor.lastrowid)
            event_type = "workspace.created"
        else:
            workspace_id = int(cast(sqlite3.Row, row)["id"])
            connection.execute(
                "UPDATE project_workspaces SET config_json=?, "
                "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
                (encoded, workspace_id),
            )
            event_type = "workspace.updated"
        _append_event(
            connection,
            project_id,
            event_type,
            {"workspace_id": workspace_id},
        )
        return _single_workspace(connection, workspace_id)


def list_workspaces(profile_root: Path, project_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        _require_project(connection, project_id)
        rows = connection.execute(
            "SELECT * FROM project_workspaces WHERE project_id=? ORDER BY lower(name), id",
            (project_id,),
        ).fetchall()
        workspaces = [_workspace_payload(cast(sqlite3.Row, row)) for row in rows]
    return {
        "family": "osca.desktop-project-workspace-list.result",
        "version": "1.0.0",
        "workspaces": workspaces,
    }


def get_workspace(profile_root: Path, workspace_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        return _single_workspace(connection, workspace_id)


def prepare_project_export(profile_root: Path, project_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        project = _project_payload(connection, project_id)
        body = {
            "family": "osca.desktop-project-manifest",
            "version": "1.0.0",
            "schema_version": _SCHEMA_VERSION,
            "project": project,
            "self_contained_package": False,
            "notes_are_user_authored": True,
            "provider_datasets_embedded": False,
        }
        digest = _sha256(_json(body).encode("utf-8"))
        manifest = {**body, "manifest_sha256": digest}
        export_dir = profile_root / ".osca" / "desktop" / "exports" / "projects"
        export_dir.mkdir(parents=True, exist_ok=True)
        path = export_dir / f"{project['project_uuid']}.manifest.json"
        path.write_text(_pretty_json(manifest), encoding="utf-8")
        _append_event(
            connection,
            project_id,
            "project.exported",
            {"manifest_path": str(path), "manifest_sha256": digest},
        )
    return {
        "family": "osca.desktop-project-export.result",
        "version": "1.0.0",
        "project_id": project_id,
        "manifest_path": str(path),
        "manifest_sha256": digest,
        "thin_manifest": True,
        "self_contained_package": False,
    }


def _transition_project(
    profile_root: Path,
    project_id: int,
    status: str,
    event_type: str,
) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        _require_project(connection, project_id)
        connection.execute(
            "UPDATE projects SET status=?, "
            "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
            (status, project_id),
        )
        _append_event(connection, project_id, event_type, {"status": status})
        return _single_project(connection, project_id)


def _database(profile_root: Path) -> Path:
    if not profile_root.is_absolute() or not profile_root.is_dir():
        raise DesktopServiceError(
            "profile_unavailable",
            "A valid absolute profile directory is required.",
        )
    directory = profile_root / ".osca" / "desktop"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "d6-projects.sqlite3"


def _connect(profile_root: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(_database(profile_root))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    current_row = connection.execute("PRAGMA user_version").fetchone()
    current = int(cast(tuple[int], current_row)[0])
    if current > _SCHEMA_VERSION:
        connection.close()
        raise DesktopServiceError(
            "project_schema_newer",
            "Project data was created by a newer OSCA version.",
        )
    if current == 0:
        connection.executescript(
            """
            CREATE TABLE projects(
              id INTEGER PRIMARY KEY,
              project_uuid TEXT NOT NULL UNIQUE,
              name TEXT NOT NULL COLLATE NOCASE UNIQUE,
              objective TEXT NOT NULL,
              horizon TEXT,
              status TEXT NOT NULL DEFAULT 'active'
                CHECK(status IN ('active', 'archived', 'deleted')),
              cloned_from_uuid TEXT,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE project_timeline(
              id INTEGER PRIMARY KEY,
              project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
              event_type TEXT NOT NULL,
              details_json TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE project_pins(
              id INTEGER PRIMARY KEY,
              project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
              pin_type TEXT NOT NULL,
              source_id TEXT NOT NULL,
              label TEXT NOT NULL,
              metadata_json TEXT NOT NULL,
              degraded_status TEXT NOT NULL DEFAULT 'available'
                CHECK(degraded_status IN ('available', 'degraded', 'broken')),
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE project_notes(
              id INTEGER PRIMARY KEY,
              project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
              title TEXT,
              body TEXT NOT NULL,
              user_authored INTEGER NOT NULL DEFAULT 1,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE project_workspaces(
              id INTEGER PRIMARY KEY,
              project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
              name TEXT NOT NULL,
              config_json TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              UNIQUE(project_id, name COLLATE NOCASE)
            );
            PRAGMA user_version=1;
            """
        )
    return connection


def _single_project(connection: sqlite3.Connection, project_id: int) -> dict[str, Any]:
    return {
        "family": "osca.desktop-project.result",
        "version": "1.0.0",
        "project": _project_payload(connection, project_id),
    }


def _project_payload(
    connection: sqlite3.Connection,
    project_id: int,
) -> dict[str, Any]:
    row = _require_project(connection, project_id)
    return {
        **_project_summary(row),
        "pins": [
            _pin_payload(cast(sqlite3.Row, pin))
            for pin in connection.execute(
                "SELECT * FROM project_pins WHERE project_id=? ORDER BY id",
                (project_id,),
            )
        ],
        "notes": [
            _note_payload(cast(sqlite3.Row, note))
            for note in connection.execute(
                "SELECT * FROM project_notes WHERE project_id=? ORDER BY id",
                (project_id,),
            )
        ],
        "workspaces": [
            _workspace_payload(cast(sqlite3.Row, workspace))
            for workspace in connection.execute(
                "SELECT * FROM project_workspaces WHERE project_id=? ORDER BY id",
                (project_id,),
            )
        ],
        "timeline": [
            _event_payload(cast(sqlite3.Row, event))
            for event in connection.execute(
                "SELECT * FROM project_timeline WHERE project_id=? ORDER BY id",
                (project_id,),
            )
        ],
    }


def _project_summary(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "project_id": int(row["id"]),
        "project_uuid": str(row["project_uuid"]),
        "name": str(row["name"]),
        "objective": str(row["objective"]),
        "horizon": row["horizon"],
        "status": str(row["status"]),
        "cloned_from_uuid": row["cloned_from_uuid"],
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }


def _single_pin(connection: sqlite3.Connection, pin_id: int) -> dict[str, Any]:
    return {
        "family": "osca.desktop-project-pin.result",
        "version": "1.0.0",
        "pin": _pin_payload(_require_pin(connection, pin_id)),
    }


def _single_note(connection: sqlite3.Connection, note_id: int) -> dict[str, Any]:
    return {
        "family": "osca.desktop-project-note.result",
        "version": "1.0.0",
        "note": _note_payload(_require_note(connection, note_id)),
    }


def _single_workspace(
    connection: sqlite3.Connection,
    workspace_id: int,
) -> dict[str, Any]:
    return {
        "family": "osca.desktop-project-workspace.result",
        "version": "1.0.0",
        "workspace": _workspace_payload(_require_workspace(connection, workspace_id)),
    }


def _pin_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "pin_id": int(row["id"]),
        "project_id": int(row["project_id"]),
        "pin_type": str(row["pin_type"]),
        "source_id": str(row["source_id"]),
        "label": str(row["label"]),
        "metadata": _load_json_object(str(row["metadata_json"]), "Project pin metadata"),
        "degraded_status": str(row["degraded_status"]),
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }


def _note_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "note_id": int(row["id"]),
        "project_id": int(row["project_id"]),
        "title": row["title"],
        "body": str(row["body"]),
        "user_authored": bool(row["user_authored"]),
        "evidence_role": "user_note",
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }


def _workspace_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "workspace_id": int(row["id"]),
        "project_id": int(row["project_id"]),
        "name": str(row["name"]),
        "config": _load_json_object(
            str(row["config_json"]),
            "Project workspace configuration",
        ),
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }


def _event_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "event_id": int(row["id"]),
        "project_id": int(row["project_id"]),
        "event_type": str(row["event_type"]),
        "details": _load_json_object(str(row["details_json"]), "Timeline details"),
        "created_at": str(row["created_at"]),
    }


def _require_project(connection: sqlite3.Connection, project_id: int) -> sqlite3.Row:
    row = connection.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
    if row is None:
        raise DesktopServiceError("project_not_found", "Research project was not found.")
    return cast(sqlite3.Row, row)


def _require_mutable_project(
    connection: sqlite3.Connection,
    project_id: int,
) -> sqlite3.Row:
    row = _require_project(connection, project_id)
    if str(row["status"]) == "deleted":
        raise DesktopServiceError(
            "project_deleted",
            "Deleted research projects cannot be mutated.",
        )
    return row


def _require_pin(connection: sqlite3.Connection, pin_id: int) -> sqlite3.Row:
    row = connection.execute("SELECT * FROM project_pins WHERE id=?", (pin_id,)).fetchone()
    if row is None:
        raise DesktopServiceError("project_pin_not_found", "Project pin was not found.")
    return cast(sqlite3.Row, row)


def _require_note(connection: sqlite3.Connection, note_id: int) -> sqlite3.Row:
    row = connection.execute("SELECT * FROM project_notes WHERE id=?", (note_id,)).fetchone()
    if row is None:
        raise DesktopServiceError("project_note_not_found", "Project note was not found.")
    return cast(sqlite3.Row, row)


def _require_workspace(
    connection: sqlite3.Connection,
    workspace_id: int,
) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM project_workspaces WHERE id=?",
        (workspace_id,),
    ).fetchone()
    if row is None:
        raise DesktopServiceError(
            "project_workspace_not_found",
            "Project workspace was not found.",
        )
    return cast(sqlite3.Row, row)


def _append_event(
    connection: sqlite3.Connection,
    project_id: int,
    event_type: str,
    details: dict[str, Any],
) -> None:
    connection.execute(
        "INSERT INTO project_timeline(project_id, event_type, details_json) "
        "VALUES (?, ?, ?)",
        (project_id, event_type, _json(details)),
    )


def _pin_type(value: str) -> str:
    normalized = _bounded_text(value, "Pin type", limit=80)
    if normalized not in _PIN_TYPES:
        raise DesktopServiceError("invalid_parameters", "Unsupported project pin type.")
    return normalized


def _degraded_status(value: str) -> str:
    normalized = _bounded_text(value, "Pin degraded status", limit=20)
    if normalized not in {"available", "degraded", "broken"}:
        raise DesktopServiceError("invalid_parameters", "Unsupported pin degraded status.")
    return normalized


def _bounded_text(value: str, field: str, *, limit: int) -> str:
    normalized = value.strip() if isinstance(value, str) else ""
    if not normalized or len(normalized) > limit:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{field} must contain 1..{limit} characters.",
        )
    return normalized


def _optional_bounded_text(value: str | None, field: str, *, limit: int) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > limit:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{field} must contain at most {limit} characters.",
        )
    return normalized


def _safe_json_object(value: dict[str, Any], field: str, *, limit: int) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesktopServiceError("invalid_parameters", f"{field} must be an object.")
    encoded = _json(value)
    if len(encoded.encode("utf-8")) > limit:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{field} exceeds {limit} bytes.",
        )
    forbidden = {
        "sql",
        "query",
        "provider_url",
        "credential",
        "secret",
        "token",
        "order",
        "broker",
        "script",
        "notebook",
    }
    sensitive_fragments = ("password", "api_key", "private_key")
    for key in _walk_keys(value):
        lowered = key.lower()
        if lowered in forbidden or any(
            fragment in lowered for fragment in sensitive_fragments
        ):
            raise DesktopServiceError(
                "invalid_parameters",
                f"{field} contains forbidden field: {key}",
            )
    return value


def _walk_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.append(str(key))
            keys.extend(_walk_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.extend(_walk_keys(nested))
    return keys


def _load_json_object(value: str, field: str) -> dict[str, Any]:
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as exc:
        raise DesktopServiceError("project_store_corrupt", f"{field} is invalid.") from exc
    if not isinstance(decoded, dict):
        raise DesktopServiceError("project_store_corrupt", f"{field} is invalid.")
    return decoded


def _json(value: dict[str, Any]) -> str:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise DesktopServiceError(
            "invalid_parameters",
            "Project data must be JSON serializable.",
        ) from exc


def _pretty_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
