from __future__ import annotations

import json
import socket
import sqlite3
import sys
from pathlib import Path
from typing import Annotated, Literal

import pyarrow
import typer
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from osca.analyst_workspace.services import AnalystWorkspaceService

_CONFIG_FILENAME = "config.json"
_SUPPORTED_PYTHON = (3, 13)
_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


class OperatorConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    family: Literal["osca.operator-config"] = "osca.operator-config"
    version: Literal["1.0.0"] = "1.0.0"
    storage_root: str = Field(min_length=1)
    workspace_host: Literal["127.0.0.1", "localhost", "::1"] = "127.0.0.1"
    workspace_port: int = Field(default=8765, ge=1, le=65535)
    network_access_enabled: Literal[False] = False
    recommendations_enabled: Literal[False] = False
    automatic_promotion_enabled: Literal[False] = False
    broker_connections_enabled: Literal[False] = False
    autonomous_execution_enabled: Literal[False] = False
    real_capital_orders_enabled: Literal[False] = False


class DoctorCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    check_id: str
    status: Literal["pass", "warning", "fail"]
    message: str
    remediation: str | None = None


def default_config(storage_root: Path, workspace_port: int = 8765) -> OperatorConfig:
    return OperatorConfig(storage_root=str(storage_root), workspace_port=workspace_port)


def initialize_profile(
    profile_root: Path,
    *,
    storage_root: Path | None = None,
    workspace_port: int = 8765,
    force: bool = False,
) -> dict[str, object]:
    root = profile_root.resolve()
    configured_storage = (storage_root or (root / "data")).resolve()
    config_path = root / _CONFIG_FILENAME
    if config_path.exists() and not force:
        raise ValueError(f"profile already initialized: {config_path}")

    root.mkdir(parents=True, exist_ok=True)
    configured_storage.mkdir(parents=True, exist_ok=True)
    try:
        config = default_config(configured_storage, workspace_port)
    except ValidationError as exc:
        raise ValueError(str(exc)) from exc
    config_path.write_text(config.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return {
        "family": "osca.operator-init.result",
        "version": "1.0.0",
        "status": "initialized",
        "profile_root": str(root),
        "config_path": str(config_path),
        "storage_root": str(configured_storage),
        "next_commands": [
            f"osca doctor --profile-root {root}",
            f"osca workspace --profile-root {root}",
        ],
        "network_access_enabled": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_orders_enabled": False,
    }


def doctor_profile(profile_root: Path, *, port: int | None = None) -> dict[str, object]:
    root = profile_root.resolve()
    checks = [_runtime_check(), _pyarrow_check()]

    config: OperatorConfig | None = None
    try:
        config = load_operator_config(root)
        checks.append(
            DoctorCheck(
                check_id="operator-config",
                status="pass",
                message="Versioned operator configuration is valid.",
            )
        )
    except ValueError as exc:
        checks.append(
            DoctorCheck(
                check_id="operator-config",
                status="fail",
                message=str(exc),
                remediation=f"Run: osca init --profile-root {root}",
            )
        )

    storage_root = Path(config.storage_root) if config else root / "data"
    checks.extend(
        (
            _storage_check(storage_root),
            _sqlite_check(),
            _port_check(config, port),
            _provider_capability_check(),
            _credential_reference_check(),
            _evidence_consistency_check(storage_root),
        )
    )

    failed = sum(check.status == "fail" for check in checks)
    warnings = sum(check.status == "warning" for check in checks)
    return {
        "family": "osca.operator-doctor.result",
        "version": "1.1.0",
        "status": "failed" if failed else ("warning" if warnings else "ready"),
        "profile_root": str(root),
        "storage_root": str(storage_root),
        "checks": [check.model_dump(mode="json") for check in checks],
        "summary": {
            "passed": len(checks) - failed - warnings,
            "warnings": warnings,
            "failed": failed,
        },
        "network_access_enabled": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_orders_enabled": False,
    }


def load_operator_config(profile_root: Path) -> OperatorConfig:
    path = profile_root.resolve() / _CONFIG_FILENAME
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        return OperatorConfig.model_validate(document)
    except OSError as exc:
        message = f"operator configuration is missing or unreadable at {path}: {exc}"
        raise ValueError(message) from exc
    except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(f"operator configuration is invalid at {path}: {exc}") from exc


def _runtime_check() -> DoctorCheck:
    supported = sys.version_info[:2] == _SUPPORTED_PYTHON
    return DoctorCheck(
        check_id="python-runtime",
        status="pass" if supported else "fail",
        message=f"Python {sys.version_info.major}.{sys.version_info.minor} detected.",
        remediation=None if supported else "Install and run OSCA with Python 3.13.",
    )


def _pyarrow_check() -> DoctorCheck:
    return DoctorCheck(
        check_id="pyarrow-runtime",
        status="pass",
        message=f"PyArrow {pyarrow.__version__} is importable.",
    )


def _storage_check(storage_root: Path) -> DoctorCheck:
    try:
        storage_root.mkdir(parents=True, exist_ok=True)
        probe = storage_root / ".doctor-write-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return DoctorCheck(
            check_id="writable-storage",
            status="fail",
            message=f"Storage root is not writable: {exc}",
            remediation="Choose a writable --storage-root and rerun osca init --force.",
        )
    return DoctorCheck(
        check_id="writable-storage",
        status="pass",
        message=f"Storage root is writable: {storage_root}",
    )


def _sqlite_check() -> DoctorCheck:
    try:
        with sqlite3.connect(":memory:") as database:
            database.execute("select 1")
    except sqlite3.Error as exc:
        return DoctorCheck(
            check_id="sqlite-runtime",
            status="fail",
            message=f"SQLite readiness failed: {exc}",
            remediation="Install a supported Python distribution with SQLite enabled.",
        )
    return DoctorCheck(
        check_id="sqlite-runtime",
        status="pass",
        message=f"SQLite {sqlite3.sqlite_version} is ready.",
    )


def _port_check(config: OperatorConfig | None, port: int | None) -> DoctorCheck:
    selected_port = port or (config.workspace_port if config else 8765)
    host = config.workspace_host if config else "127.0.0.1"
    if host not in _LOOPBACK_HOSTS:
        return DoctorCheck(
            check_id="workspace-port",
            status="fail",
            message=f"Workspace host is not loopback-only: {host}",
            remediation="Reinitialize the profile with a supported loopback configuration.",
        )
    if _port_available(host, selected_port):
        return DoctorCheck(
            check_id="workspace-port",
            status="pass",
            message=f"Workspace endpoint {host}:{selected_port} is available.",
        )
    return DoctorCheck(
        check_id="workspace-port",
        status="warning",
        message=f"Workspace endpoint {host}:{selected_port} is already in use.",
        remediation="Choose another port with osca workspace --port PORT.",
    )


def _provider_capability_check() -> DoctorCheck:
    return DoctorCheck(
        check_id="provider-capability",
        status="pass",
        message=(
            "Kraken public spot OHLC is admitted for explicit internal-use acquisition; "
            "equity acquisition remains policy-blocked with CSV/Parquet fallback."
        ),
    )


def _credential_reference_check() -> DoctorCheck:
    return DoctorCheck(
        check_id="credential-reference",
        status="pass",
        message=(
            "The canonical no-cost Kraken path requires no credential materialization. "
            "Authenticated providers remain disabled until separately admitted."
        ),
    )


def _evidence_consistency_check(storage_root: Path) -> DoctorCheck:
    try:
        snapshot = AnalystWorkspaceService().snapshot(storage_root)
    except (OSError, sqlite3.Error, ValueError) as exc:
        return DoctorCheck(
            check_id="evidence-consistency",
            status="fail",
            message=f"Retained evidence could not be inspected: {exc}",
            remediation="Inspect the configured storage root and restore a valid backup if needed.",
        )
    if snapshot.warnings:
        return DoctorCheck(
            check_id="evidence-consistency",
            status="warning",
            message=f"Workspace reported {len(snapshot.warnings)} evidence warning(s).",
            remediation="Run osca workspace --snapshot and inspect the warning details.",
        )
    if snapshot.total_items == 0:
        return DoctorCheck(
            check_id="evidence-consistency",
            status="warning",
            message="No retained research evidence is present yet.",
            remediation="Acquire or import data, then run osca research-pipeline.",
        )
    return DoctorCheck(
        check_id="evidence-consistency",
        status="pass",
        message=f"Workspace discovered {snapshot.total_items} retained item(s) without warnings.",
    )


def _port_available(host: str, port: int) -> bool:
    if port < 1 or port > 65535:
        return False
    family = socket.AF_INET6 if host == "::1" else socket.AF_INET
    with socket.socket(family, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind((host, port))
        except OSError:
            return False
    return True


def init_command(
    profile_root: Annotated[Path, typer.Option("--profile-root")] = Path(".osca"),
    storage_root: Annotated[Path | None, typer.Option("--storage-root")] = None,
    workspace_port: Annotated[int, typer.Option("--workspace-port")] = 8765,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Initialize a safe local OSCA operator profile."""
    try:
        result = initialize_profile(
            profile_root,
            storage_root=storage_root,
            workspace_port=workspace_port,
            force=force,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(json.dumps(result, indent=2, sort_keys=True))


def doctor_command(
    profile_root: Annotated[Path, typer.Option("--profile-root")] = Path(".osca"),
    port: Annotated[int | None, typer.Option("--port")] = None,
) -> None:
    """Run structured local readiness and corrective diagnostics."""
    result = doctor_profile(profile_root, port=port)
    typer.echo(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] == "failed":
        raise typer.Exit(1)
