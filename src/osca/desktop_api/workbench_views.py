"""Profile-scoped declarative saved views for the D5 workbench."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from osca.desktop_api.service import DesktopServiceError

_SCHEMA_VERSION = 1


def list_views(profile_root: Path) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        rows = connection.execute(
            "SELECT id, name, description, config_json, created_at, updated_at "
            "FROM workbench_views ORDER BY lower(name), id"
        ).fetchall()
        views = [_row_payload(row) for row in rows]
    return {
        "family": "osca.desktop-workbench-view-list.result",
        "version": "1.0.0",
        "views": views,
        "schema_version": _SCHEMA_VERSION,
    }


def get_view(profile_root: Path, view_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        row = _require_view(connection, view_id)
        payload = _row_payload(row)
    return _single_result(payload)


def create_view(
    profile_root: Path,
    *,
    name: str,
    description: str | None,
    config: dict[str, Any],
) -> dict[str, Any]:
    normalized_name = _view_name(name)
    normalized_description = _description(description)
    normalized_config = _config(config)
    with _connect(profile_root) as connection:
        try:
            cursor = connection.execute(
                "INSERT INTO workbench_views(name, description, config_json) VALUES (?, ?, ?)",
                (normalized_name, normalized_description, _json(normalized_config)),
            )
        except sqlite3.IntegrityError as exc:
            raise DesktopServiceError(
                "workbench_view_conflict",
                "A saved workbench view with that name already exists.",
            ) from exc
        assert cursor.lastrowid is not None
        row = _require_view(connection, int(cursor.lastrowid))
        payload = _row_payload(row)
    return _single_result(payload)


def update_view(
    profile_root: Path,
    *,
    view_id: int,
    description: str | None,
    config: dict[str, Any],
) -> dict[str, Any]:
    normalized_description = _description(description)
    normalized_config = _config(config)
    with _connect(profile_root) as connection:
        cursor = connection.execute(
            "UPDATE workbench_views SET description=?, config_json=?, "
            "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
            (normalized_description, _json(normalized_config), view_id),
        )
        if cursor.rowcount != 1:
            raise DesktopServiceError("workbench_view_not_found", "Saved workbench view was not found.")
        payload = _row_payload(_require_view(connection, view_id))
    return _single_result(payload)


def rename_view(profile_root: Path, *, view_id: int, name: str) -> dict[str, Any]:
    normalized_name = _view_name(name)
    with _connect(profile_root) as connection:
        try:
            cursor = connection.execute(
                "UPDATE workbench_views SET name=?, "
                "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
                (normalized_name, view_id),
            )
        except sqlite3.IntegrityError as exc:
            raise DesktopServiceError(
                "workbench_view_conflict",
                "A saved workbench view with that name already exists.",
            ) from exc
        if cursor.rowcount != 1:
            raise DesktopServiceError("workbench_view_not_found", "Saved workbench view was not found.")
        payload = _row_payload(_require_view(connection, view_id))
    return _single_result(payload)


def delete_view(profile_root: Path, view_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        cursor = connection.execute("DELETE FROM workbench_views WHERE id=?", (view_id,))
        if cursor.rowcount != 1:
            raise DesktopServiceError("workbench_view_not_found", "Saved workbench view was not found.")
    return {
        "family": "osca.desktop-workbench-view-delete.result",
        "version": "1.0.0",
        "deleted": True,
        "view_id": view_id,
    }


def _database(profile_root: Path) -> Path:
    if not profile_root.is_absolute() or not profile_root.is_dir():
        raise DesktopServiceError("profile_unavailable", "A valid absolute profile directory is required.")
    directory = profile_root / ".osca" / "desktop"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "d5-workbench.sqlite3"


def _connect(profile_root: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(_database(profile_root))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    current = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if current > _SCHEMA_VERSION:
        connection.close()
        raise DesktopServiceError(
            "workbench_schema_newer",
            "Saved workbench data was created by a newer OSCA version.",
        )
    if current == 0:
        connection.executescript(
            """
            CREATE TABLE workbench_views(
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL COLLATE NOCASE UNIQUE,
              description TEXT,
              config_json TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            PRAGMA user_version=1;
            """
        )
    return connection


def _require_view(connection: sqlite3.Connection, view_id: int) -> sqlite3.Row:
    row = connection.execute(
        "SELECT id, name, description, config_json, created_at, updated_at "
        "FROM workbench_views WHERE id=?",
        (view_id,),
    ).fetchone()
    if row is None:
        raise DesktopServiceError("workbench_view_not_found", "Saved workbench view was not found.")
    return row


def _row_payload(row: sqlite3.Row) -> dict[str, Any]:
    try:
        config = json.loads(str(row["config_json"]))
    except json.JSONDecodeError as exc:
        raise DesktopServiceError(
            "workbench_view_corrupt",
            "Saved workbench view configuration is invalid.",
        ) from exc
    if not isinstance(config, dict):
        raise DesktopServiceError(
            "workbench_view_corrupt",
            "Saved workbench view configuration is invalid.",
        )
    return {
        "view_id": int(row["id"]),
        "name": str(row["name"]),
        "description": row["description"],
        "config_version": "1.0.0",
        "config": config,
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }


def _single_result(view: dict[str, Any]) -> dict[str, Any]:
    return {
        "family": "osca.desktop-workbench-view.result",
        "version": "1.0.0",
        "view": view,
    }


def _view_name(value: str) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > 80:
        raise DesktopServiceError(
            "invalid_parameters",
            "Saved view name must contain 1..80 characters.",
        )
    return normalized


def _description(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if len(normalized) > 500:
        raise DesktopServiceError(
            "invalid_parameters",
            "Saved view description must contain at most 500 characters.",
        )
    return normalized or None


def _config(value: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesktopServiceError("invalid_parameters", "config must be an object")
    encoded = _json(value)
    if len(encoded.encode("utf-8")) > 32_768:
        raise DesktopServiceError("invalid_parameters", "Saved view configuration exceeds 32 KiB.")
    forbidden = {"sql", "query", "provider_url", "credential", "secret", "token", "order", "broker"}
    for key in _walk_keys(value):
        lowered = key.lower()
        if lowered in forbidden or any(term in lowered for term in ("password", "api_key", "private_key")):
            raise DesktopServiceError(
                "invalid_parameters",
                f"Saved view configuration contains forbidden field: {key}",
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


def _json(value: dict[str, Any]) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise DesktopServiceError(
            "invalid_parameters",
            "Saved view configuration must be JSON serializable.",
        ) from exc
