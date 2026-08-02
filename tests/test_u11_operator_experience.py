from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from osca.cli import app
from osca.operator_aliases import analyze_command, backtest_command, import_data_command
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


def test_config_rejects_unsafe_or_unknown_fields(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile)
    path = profile / "config.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["network_access_enabled"] = True
    document["unknown_setting"] = "not-supported"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match="operator configuration is invalid"):
        load_operator_config(profile)


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


def test_doctor_reports_provider_credentials_and_evidence_state(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile, workspace_port=54321)

    result = doctor_profile(profile, port=54322)
    checks = {check["check_id"]: check for check in result["checks"]}

    assert result["status"] in {"ready", "warning"}
    assert checks["operator-config"]["status"] == "pass"
    assert checks["writable-storage"]["status"] == "pass"
    assert checks["sqlite-runtime"]["status"] == "pass"
    assert checks["pyarrow-runtime"]["status"] == "pass"
    assert checks["provider-capability"]["status"] == "pass"
    assert "Kraken" in checks["provider-capability"]["message"]
    assert checks["credential-reference"]["status"] == "pass"
    assert checks["evidence-consistency"]["status"] == "warning"


def test_doctor_detects_workspace_evidence_warnings(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    initialize_profile(profile)
    config = load_operator_config(profile)
    malformed = Path(config.storage_root) / "research-evidence" / "run" / "diagnostic.json"
    malformed.parent.mkdir(parents=True)
    malformed.write_text("not-json", encoding="utf-8")

    result = doctor_profile(profile, port=54324)
    checks = {check["check_id"]: check for check in result["checks"]}

    assert checks["evidence-consistency"]["status"] == "warning"
    assert "warning" in checks["evidence-consistency"]["message"].lower()


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
    assert doctor_payload["version"] == "1.1.0"

    help_result = runner.invoke(app, ["--help"])
    assert help_result.exit_code == 0
    for command in (
        "init",
        "doctor",
        "workspace",
        "historical-data",
        "import-data",
        "analyze",
        "backtest",
        "research-pipeline",
    ):
        assert command in help_result.output


def test_canonical_aliases_delegate_to_compatibility_commands(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[list[str]] = []

    def capture(command: list[str]) -> None:
        observed.append(command)

    monkeypatch.setattr("osca.operator_aliases._run_primary", capture)

    input_file = tmp_path / "history.csv"
    payload_file = tmp_path / "payload.parquet"
    import_data_command(input_file, "AAPL", "1d", tmp_path / "data", "csv")
    analyze_command(payload_file, "AAPL", "1d")
    backtest_command(payload_file, "AAPL", "1d")

    assert observed[0][:4] == ["local-ohlcv-import", str(input_file), "AAPL", "1d"]
    assert observed[1][:4] == ["demo-research-report", str(payload_file), "AAPL", "1d"]
    assert observed[2][:4] == ["backtest-paper-run", str(payload_file), "AAPL", "1d"]


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
