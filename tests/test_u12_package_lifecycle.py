from __future__ import annotations

import json
import zipfile
from pathlib import Path

from typer.testing import CliRunner

from osca.cli import app
from osca.operator_experience import initialize_profile
from osca.package_lifecycle import create_verified_backup, inspect_profile, version_report

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
    with zipfile.ZipFile(output) as archive:
        manifest = json.loads(archive.read("backup-manifest.json"))
        paths = {item["path"] for item in manifest["files"]}
        assert paths == {"config.json", "data/evidence.json"}
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
