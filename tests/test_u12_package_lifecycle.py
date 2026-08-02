from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from osca.cli import app
from osca.operator_experience import initialize_profile
from osca.package_lifecycle import (
    create_verified_backup,
    inspect_profile,
    restore_verified_backup,
    upgrade_profile,
    validate_backup,
    version_report,
)

runner = CliRunner()


def test_version_report_preserves_safety_boundaries() -> None:
    report = version_report()

    assert report["family"] == "osca.package-version.report"
    assert report["osca_version"]
    assert report["python_version"]
    assert report["recommendations_enabled"] is False
    assert report["broker_connections_enabled"] is False
    assert report["real_capital_orders_enabled"] is False


def test_lifecycle_inspection_is_non_mutating(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile, workspace_port=54321)

    report = inspect_profile(profile)

    assert report["status"] == "compatible"
    assert report["mutation_performed"] is False
    assert report["summary"]["failed"] == 0


def test_incompatible_profile_fails_closed(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    profile.mkdir()

    result = runner.invoke(
        app,
        ["lifecycle", "inspect", "--profile-root", str(profile)],
    )

    assert result.exit_code == 1
    document = json.loads(result.output)
    assert document["status"] == "incompatible"
    assert document["mutation_performed"] is False


def test_verified_backup_retains_manifest_and_digests(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile, workspace_port=54321)
    retained = profile / "data" / "evidence.json"
    retained.write_text('{"status":"retained"}\n', encoding="utf-8")
    output = tmp_path / "backup.zip"

    result = create_verified_backup(profile, output)

    assert result["status"] == "verified"
    assert result["file_count"] == 2
    assert result["mutation_performed"] is False
    assert output.is_file()
    manifest = validate_backup(output)
    assert {item.path for item in manifest.files} == {"config.json", "data/evidence.json"}
    with zipfile.ZipFile(output) as archive:
        assert archive.read("data/evidence.json") == retained.read_bytes()


def test_backup_refuses_incompatible_profile(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    profile.mkdir()

    result = runner.invoke(
        app,
        [
            "lifecycle",
            "backup",
            "--profile-root",
            str(profile),
            "--output",
            str(tmp_path / "backup.zip"),
        ],
    )

    assert result.exit_code != 0
    assert "backup refused before mutation" in result.output
    assert not (tmp_path / "backup.zip").exists()


def test_restore_rejects_nonempty_destination_without_replace(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile, workspace_port=54321)
    backup = tmp_path / "backup.zip"
    create_verified_backup(profile, backup)
    destination = tmp_path / "destination"
    destination.mkdir()
    (destination / "unrelated.txt").write_text("preserve", encoding="utf-8")

    with pytest.raises(ValueError, match="not empty"):
        restore_verified_backup(backup, destination)

    assert (destination / "unrelated.txt").read_text(encoding="utf-8") == "preserve"


def test_restore_recreates_verified_profile_atomically(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile, workspace_port=54321)
    evidence = profile / "data" / "evidence.json"
    evidence.write_text('{"id":"original"}\n', encoding="utf-8")
    backup = tmp_path / "backup.zip"
    create_verified_backup(profile, backup)
    evidence.write_text('{"id":"changed"}\n', encoding="utf-8")

    result = restore_verified_backup(backup, profile, replace=True)

    assert result["status"] == "restored"
    assert json.loads(evidence.read_text(encoding="utf-8"))["id"] == "original"
    assert inspect_profile(profile)["status"] == "compatible"


def test_backup_validation_rejects_path_traversal(tmp_path: Path) -> None:
    backup = tmp_path / "malicious.zip"
    manifest = {
        "family": "osca.profile-backup.manifest",
        "version": "1.0.0",
        "created_at": "2026-08-02T00:00:00Z",
        "osca_version": "0.1.0.dev0",
        "profile_root": "/tmp/profile",
        "files": [
            {
                "path": "../escaped.txt",
                "size": 7,
                "sha256": "239f59ed55e737c77147cf55ad0c1b030b6d7ee748a7426952f9b852d5a935e5",
            }
        ],
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_orders_enabled": False,
    }
    with zipfile.ZipFile(backup, "w") as archive:
        archive.writestr("../escaped.txt", b"payload")
        archive.writestr("backup-manifest.json", json.dumps(manifest))

    with pytest.raises(ValueError, match="unsafe backup member path"):
        validate_backup(backup)


def test_upgrade_requires_backup_and_records_lifecycle_state(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile, workspace_port=54321)
    backup = tmp_path / "pre-upgrade.zip"

    result = upgrade_profile(profile, backup, "0.2.0")

    assert result["status"] == "upgraded"
    assert backup.is_file()
    state = json.loads((profile / "lifecycle" / "state.json").read_text(encoding="utf-8"))
    assert state["installed_osca_version"] == "0.2.0"
    assert state["backup_sha256"] == result["backup_sha256"]


def test_failed_upgrade_restores_pre_upgrade_digests(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile, workspace_port=54321)
    evidence = profile / "data" / "evidence.json"
    evidence.write_text('{"id":"accepted"}\n', encoding="utf-8")
    backup = tmp_path / "pre-upgrade.zip"

    def fail_after_mutation(root: Path) -> None:
        (root / "config.json").write_text("corrupt", encoding="utf-8")
        (root / "data" / "evidence.json").unlink()
        raise RuntimeError("simulated migration failure")

    result = upgrade_profile(profile, backup, "0.2.0", mutation=fail_after_mutation)

    assert result["status"] == "recovered"
    assert result["pre_upgrade_digests_preserved"] is True
    assert json.loads(evidence.read_text(encoding="utf-8"))["id"] == "accepted"
    assert inspect_profile(profile)["status"] == "compatible"
    assert not (profile / "lifecycle" / "state.json").exists()
