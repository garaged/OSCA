from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from osca.cli import app
from osca.operator_experience import doctor_profile, initialize_profile, load_operator_config

runner = CliRunner()


def test_init_creates_safe_versioned_profile(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    result = initialize_profile(profile)
    config = load_operator_config(profile)

    assert result["status"] == "initialized"
    assert config.family == "osca.operator-config"
    assert config.version == "1.0.0"
    assert config.workspace_host == "127.0.0.1"
    assert config.network_access_enabled is False
    assert config.recommendations_enabled is False
    assert config.automatic_promotion_enabled is False
    assert config.broker_connections_enabled is False
    assert config.autonomous_execution_enabled is False
    assert config.real_capital_orders_enabled is False
    assert Path(config.storage_root).is_dir()


def test_init_refuses_overwrite_without_force(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile)

    result = runner.invoke(app, ["init", "--profile-root", str(profile)])

    assert result.exit_code != 0
    assert "profile already initialized" in result.output


def test_doctor_reports_corrective_failure_before_init(tmp_path: Path) -> None:
    result = doctor_profile(tmp_path / "missing")
    checks = {check["check_id"]: check for check in result["checks"]}

    assert result["status"] == "failed"
    assert checks["operator-config"]["status"] == "fail"
    assert "osca init" in checks["operator-config"]["remediation"]
    assert result["network_access_enabled"] is False
    assert result["recommendations_enabled"] is False
    assert result["broker_connections_enabled"] is False
    assert result["real_capital_orders_enabled"] is False


def test_doctor_passes_initialized_profile(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile, workspace_port=54321)

    result = doctor_profile(profile, port=54322)
    checks = {check["check_id"]: check for check in result["checks"]}

    assert result["status"] in {"ready", "warning"}
    assert checks["operator-config"]["status"] == "pass"
    assert checks["writable-storage"]["status"] == "pass"
    assert checks["sqlite-runtime"]["status"] == "pass"
    assert checks["pyarrow-runtime"]["status"] == "pass"


def test_primary_cli_exposes_u11_commands(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    init_result = runner.invoke(app, ["init", "--profile-root", str(profile)])
    assert init_result.exit_code == 0
    payload = json.loads(init_result.output)
    assert payload["family"] == "osca.operator-init.result"

    doctor_result = runner.invoke(
        app,
        ["doctor", "--profile-root", str(profile), "--port", "54323"],
    )
    assert doctor_result.exit_code == 0
    doctor_payload = json.loads(doctor_result.output)
    assert doctor_payload["family"] == "osca.operator-doctor.result"

    help_result = runner.invoke(app, ["--help"])
    assert help_result.exit_code == 0
    for command in ("init", "doctor", "workspace", "historical-data", "research-pipeline"):
        assert command in help_result.output


def test_workspace_rejects_non_loopback_host(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile)

    result = runner.invoke(
        app,
        [
            "workspace",
            "--profile-root",
            str(profile),
            "--host",
            "0.0.0.0",
            "--snapshot",
        ],
    )

    assert result.exit_code != 0
    assert "loopback-only" in result.output
