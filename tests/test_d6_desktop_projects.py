from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, cast

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.d6_service import D6DesktopApplicationService


def _call(
    service: D6DesktopApplicationService,
    method: str,
    params: dict[str, Any] | None = None,
) -> DesktopResponse:
    return service.handle(
        DesktopRequest(
            request_id=f"test-{method}",
            method=method,
            params=params or {},
        )
    )


def _profile(tmp_path: Path) -> tuple[D6DesktopApplicationService, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    service = D6DesktopApplicationService(state_root=tmp_path / "state")
    profile_root = tmp_path / "profile"
    assert _call(service, "profile.create", {"profile_root": str(profile_root)}).status == "ok"
    return service, profile_root


def _project(service: D6DesktopApplicationService, profile_root: Path) -> dict[str, Any]:
    response = _call(
        service,
        "project.create",
        {
            "profile_root": str(profile_root),
            "name": "AAPL earnings thesis",
            "objective": "Evaluate retained AAPL evidence before earnings.",
            "horizon": "2026 Q1",
        },
    )
    assert response.status == "ok", response.error
    assert response.result is not None
    return cast(dict[str, Any], response.result["project"])


def test_project_lifecycle_restart_archive_restore_and_clone(tmp_path: Path) -> None:
    service, profile_root = _profile(tmp_path)
    project = _project(service, profile_root)
    project_id = project["project_id"]
    project_uuid = project["project_uuid"]

    updated = _call(
        service,
        "project.update",
        {
            "profile_root": str(profile_root),
            "project_id": project_id,
            "name": "AAPL revised thesis",
            "objective": "Review updated local evidence.",
        },
    )
    assert updated.status == "ok"
    archived = _call(
        service,
        "project.archive",
        {"profile_root": str(profile_root), "project_id": project_id},
    )
    assert archived.result is not None
    assert archived.result["project"]["status"] == "archived"
    active_only = _call(service, "project.list", {"profile_root": str(profile_root)})
    assert active_only.result is not None
    assert active_only.result["projects"] == []

    restarted = D6DesktopApplicationService(state_root=tmp_path / "state-restarted")
    restored = _call(
        restarted,
        "project.restore",
        {"profile_root": str(profile_root), "project_id": project_id},
    )
    assert restored.result is not None
    assert restored.result["project"]["status"] == "active"

    cloned = _call(
        restarted,
        "project.clone",
        {
            "profile_root": str(profile_root),
            "project_id": project_id,
            "name": "AAPL thesis clone",
        },
    )
    assert cloned.status == "ok"
    assert cloned.result is not None
    clone = cloned.result["project"]
    assert clone["project_id"] != project_id
    assert clone["project_uuid"] != project_uuid
    assert clone["cloned_from_uuid"] == project_uuid
    assert [event["event_type"] for event in clone["timeline"]] == ["project.cloned"]


def test_project_pins_notes_workspaces_and_manifest_export(tmp_path: Path) -> None:
    service, profile_root = _profile(tmp_path)
    project = _project(service, profile_root)
    project_id = project["project_id"]

    pin = _call(
        service,
        "project.pin.add",
        {
            "profile_root": str(profile_root),
            "project_id": project_id,
            "pin_type": "asset",
            "source_id": "equity:XNAS:AAPL",
            "label": "AAPL",
            "metadata": {"currency": "USD"},
        },
    )
    assert pin.status == "ok"
    assert pin.result is not None
    pin_id = pin.result["pin"]["pin_id"]
    degraded = _call(
        service,
        "project.pin.update",
        {
            "profile_root": str(profile_root),
            "pin_id": pin_id,
            "degraded_status": "broken",
        },
    )
    assert degraded.result is not None
    assert degraded.result["pin"]["degraded_status"] == "broken"

    note = _call(
        service,
        "project.note.add",
        {
            "profile_root": str(profile_root),
            "project_id": project_id,
            "title": "Initial read",
            "body": "User note about evidence, not a recommendation.",
        },
    )
    assert note.result is not None
    assert note.result["note"]["evidence_role"] == "user_note"
    assert note.result["note"]["user_authored"] is True

    workspace = _call(
        service,
        "project.workspace.save",
        {
            "profile_root": str(profile_root),
            "project_id": project_id,
            "name": "Daily evidence layout",
            "config": {"selected_pin_id": pin_id, "visible_panes": ["pins", "timeline"]},
        },
    )
    assert workspace.result is not None
    assert workspace.result["workspace"]["config"]["selected_pin_id"] == pin_id

    exported = _call(
        service,
        "project.export.prepare",
        {"profile_root": str(profile_root), "project_id": project_id},
    )
    assert exported.status == "ok", exported.error
    assert exported.result is not None
    assert exported.result["thin_manifest"] is True
    manifest_path = Path(exported.result["manifest_path"])
    assert profile_root in manifest_path.parents
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["self_contained_package"] is False
    assert manifest["notes_are_user_authored"] is True
    assert manifest["project"]["pins"][0]["degraded_status"] == "broken"
    assert manifest["project"]["notes"][0]["evidence_role"] == "user_note"
    assert manifest["manifest_sha256"] == exported.result["manifest_sha256"]


def test_project_rejects_secret_or_executable_fields(tmp_path: Path) -> None:
    service, profile_root = _profile(tmp_path)
    project = _project(service, profile_root)

    rejected_pin = _call(
        service,
        "project.pin.add",
        {
            "profile_root": str(profile_root),
            "project_id": project["project_id"],
            "pin_type": "external_reference",
            "source_id": "local-note",
            "label": "unsafe",
            "metadata": {"api_key": "secret"},
        },
    )
    assert rejected_pin.status == "error"
    assert rejected_pin.error is not None
    assert rejected_pin.error.code == "invalid_parameters"

    rejected_workspace = _call(
        service,
        "project.workspace.save",
        {
            "profile_root": str(profile_root),
            "project_id": project["project_id"],
            "name": "unsafe",
            "config": {"notebook": "run this"},
        },
    )
    assert rejected_workspace.status == "error"
    assert rejected_workspace.error is not None
    assert rejected_workspace.error.code == "invalid_parameters"


def test_project_profile_isolation_and_newer_schema_rejection(tmp_path: Path) -> None:
    service, first = _profile(tmp_path / "first")
    project = _project(service, first)
    second_parent = tmp_path / "second"
    second_parent.mkdir(parents=True, exist_ok=True)
    second = second_parent / "profile"
    assert _call(service, "profile.create", {"profile_root": str(second)}).status == "ok"

    other = _call(service, "project.list", {"profile_root": str(second)})
    assert other.result is not None
    assert other.result["projects"] == []

    database = first / ".osca" / "desktop" / "d6-projects.sqlite3"
    assert database.is_file()
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA user_version=99")

    response = _call(
        service,
        "project.get",
        {"profile_root": str(first), "project_id": project["project_id"]},
    )
    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "project_schema_newer"


def test_deleted_project_cannot_be_mutated_and_remains_auditable(tmp_path: Path) -> None:
    service, profile_root = _profile(tmp_path)
    project = _project(service, profile_root)
    project_id = project["project_id"]

    deleted = _call(
        service,
        "project.delete",
        {"profile_root": str(profile_root), "project_id": project_id},
    )
    assert deleted.result is not None
    assert deleted.result["project"]["status"] == "deleted"

    mutate = _call(
        service,
        "project.note.add",
        {
            "profile_root": str(profile_root),
            "project_id": project_id,
            "body": "Should fail",
        },
    )
    assert mutate.status == "error"
    assert mutate.error is not None
    assert mutate.error.code == "project_deleted"

    listed = _call(
        service,
        "project.list",
        {"profile_root": str(profile_root), "include_deleted": True},
    )
    assert listed.result is not None
    assert listed.result["projects"][0]["status"] == "deleted"
