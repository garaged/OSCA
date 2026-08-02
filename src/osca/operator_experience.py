from __future__ import annotations

import json
import os
import socket
import sqlite3
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Annotated, Literal

import pyarrow
import typer

_CONFIG_FILENAME = "config.json"
_SUPPORTED_PYTHON = (3, 13)


@dataclass(frozen=True)
class OperatorConfig:
    family: str
    version: str
    storage_root: str
    workspace_host: str
    workspace_port: int
    network_access_enabled: bool
    recommendations_enabled: bool
    automatic_promotion_enabled: bool
    broker_connections_enabled: bool
    autonomous_execution_enabled: bool
    real_capital_orders_enabled: bool


@dataclass(frozen=True)
class DoctorCheck:
    check_id: str
    status: Literal["pass", "warning", "fail"]
    message: str
    remediation: str | None = None


def default_config(storage_root: Path, workspace_port: int = 8765) -> OperatorConfig:
    return OperatorConfig(
        family="osca.operator-config",
        version="1.0.0",
        storage_root=str(storage_root),
        workspace_host="127.0.0.1",
        workspace_port=workspace_port,
        network_access_enabled=False,
        recommendations_enabled=False,
        automatic_promotion_enabled=False,
        broker_connections_enabled=False,
        autonomous_execution_enabled=False,
        real_capital_orders_enabled=False,
    )


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
    if workspace_port < 1 or workspace_port > 65535:
        raise ValueError("workspace port must be between 1 and 65535")

    root.mkdir(parents=True, exist_ok=True)
    configured_storage.mkdir(parents=True, exist_ok=True)
    config = default_config(configured_storage, workspace_port)
    config_path.write_text(json.dumps(asdict(config), indent=2, sort_keys=True) + "\n")
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
    config_path = root / _CONFIG_FILENAME
    checks: list[DoctorCheck] = []

    checks.append(
        DoctorCheck(
            check_id="python-runtime",
            status="pass" if sys.version_info[:2] == _SUPPORTED_PYTHON else "fail",
            message=f"Python {sys.version_info.major}.{sys.version_info.minor} detected.",
            remediation=(
                None
                if sys.version_info[:2] == _SUPPORTED_PYTHON
                else "Install and run OSCA with Python 3.13."
            ),
        )
    )
    checks.append(
        DoctorCheck(
            check_id="pyarrow-runtime",
            status="pass",
            message=f"PyArrow {pyarrow.__version__} is importable.",
        )
    )

    config: dict[str, object] | None = None
    if not config_path.is_file():
        checks.append(
            DoctorCheck(
                check_id="operator-config",
                status="fail",
                message=f"Operator configuration is missing at {config_path}.",
                remediation=f"Run: osca init --profile-root {root}",
            )
        )
    else:
        try:
            loaded = json.loads(config_path.read_text())
            if not isinstance(loaded, dict):
                raise ValueError("configuration must be a JSON object")
            config = loaded
            checks.append(
                DoctorCheck(
                    check_id="operator-config",
                    status="pass",
                    message="Versioned operator configuration is readable.",
                )
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            checks.append(
                DoctorCheck(
                    check_id="operator-config",
                    status="fail",
                    message=f"Operator configuration is invalid: {exc}",
                    remediation="Move the invalid file aside and rerun osca init.",
                )
            )

    storage_root = Path(str(config.get("storage_root"))) if config else root / "data"
    try:
        storage_root.mkdir(parents=True, exist_ok=True)
        probe = storage_root / ".doctor-write-probe"
        probe.write_text("ok")
        probe.unlink()
        checks.append(
            DoctorCheck(
                check_id="writable-storage",
                status="pass",
                message=f"Storage root is writable: {storage_root}",
            )
        )
    except OSError as exc:
        checks.append(
            DoctorCheck(
                check_id="writable-storage",
                status="fail",
                message=f"Storage root is not writable: {exc}",
                remediation="Choose a writable --storage-root and rerun osca init --force.",
            )
        )

    try:
        database = sqlite3.connect(":memory:")
        database.execute("select 1")
        database.close()
        checks.append(
            DoctorCheck(
                check_id="sqlite-runtime",
                status="pass",
                message=f"SQLite {sqlite3.sqlite_version} is ready.",
            )
        )
    except sqlite3.Error as exc:
        checks.append(
            DoctorCheck(
                check_id="sqlite-runtime",
                status="fail",
                message=f"SQLite readiness failed: {exc}",
                remediation="Install a supported Python distribution with SQLite enabled.",
            )
        )

    selected_port = port or int(config.get("workspace_port", 8765) if config else 8765)
    host = str(config.get("workspace_host", "127.0.0.1") if config else "127.0.0.1")
    if _port_available(host, selected_port):
        checks.append(
            DoctorCheck(
                check_id="workspace-port",
                status="pass",
                message=f"Workspace endpoint {host}:{selected_port} is available.",
            )
        )
    else:
        checks.append(
            DoctorCheck(
                check_id="workspace-port",
                status="warning",
                message=f"Workspace endpoint {host}:{selected_port} is already in use.",
                remediation="Choose another port with osca workspace --port PORT.",
            )
        )

    evidence_directories = (
        storage_root / "historical-acquisition",
        storage_root / "research-evidence",
        storage_root / "payloads",
    )
    retained_count = sum(
        1 for directory in evidence_directories if directory.exists() for _ in directory.rglob("*")
    )
    checks.append(
        DoctorCheck(
            check_id="retained-evidence",
            status="pass" if retained_count else "warning",
            message=(
                f"Retained evidence entries discovered: {retained_count}."
                if retained_count
                else "No retained research evidence is present yet."
            ),
            remediation=(
                None
                if retained_count
                else "Acquire or import data, then run osca research-pipeline."
            ),
        )
    )

    failed = sum(check.status == "fail" for check in checks)
    warnings = sum(check.status == "warning" for check in checks)
    return {
        "family": "osca.operator-doctor.result",
        "version": "1.0.0",
        "status": "failed" if failed else ("warning" if warnings else "ready"),
        "profile_root": str(root),
        "storage_root": str(storage_root),
        "checks": [asdict(check) for check in checks],
        "summary": {"passed": len(checks) - failed - warnings, "warnings": warnings, "failed": failed},
        "network_access_enabled": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_orders_enabled": False,
    }


def load_operator_config(profile_root: Path) -> OperatorConfig:
    path = profile_root.resolve() / _CONFIG_FILENAME
    try:
        document = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load operator configuration: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError("operator configuration must be a JSON object")
    return OperatorConfig(**document)


def _port_available(host: str, port: int) -> bool:
    if port < 1 or port > 65535:
        return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
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
