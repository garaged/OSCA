from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import zipfile
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from osca.operator_experience import load_operator_config

_SUPPORTED_PLATFORMS = {("Darwin", "arm64"), ("Linux", "x86_64")}


class CompatibilityCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    check_id: str
    status: Literal["pass", "warning", "fail"]
    message: str
    remediation: str | None = None


def package_version() -> str:
    try:
        return version("osca")
    except PackageNotFoundError:
        return "0+unknown"


def version_report() -> dict[str, object]:
    system = platform.system()
    machine = platform.machine()
    return {
        "family": "osca.package-version.report",
        "version": "1.0.0",
        "osca_version": package_version(),
        "python_version": platform.python_version(),
        "platform_system": system,
        "platform_machine": machine,
        "supported_platform": (system, machine) in _SUPPORTED_PLATFORMS,
        "build_commit": os.environ.get("OSCA_BUILD_COMMIT"),
        "build_source": os.environ.get("OSCA_BUILD_SOURCE"),
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_orders_enabled": False,
    }


def inspect_profile(profile_root: Path) -> dict[str, object]:
    root = profile_root.resolve()
    checks: list[CompatibilityCheck] = []
    system = platform.system()
    machine = platform.machine()
    supported = (system, machine) in _SUPPORTED_PLATFORMS
    checks.append(
        CompatibilityCheck(
            check_id="supported-platform",
            status="pass" if supported else "fail",
            message=f"Detected {system} {machine}.",
            remediation=None
            if supported
            else "Use macOS Apple Silicon or Linux x86-64 for the supported U12 lifecycle.",
        )
    )
    python_supported = sys.version_info[:2] == (3, 13)
    checks.append(
        CompatibilityCheck(
            check_id="python-runtime",
            status="pass" if python_supported else "fail",
            message=f"Python {sys.version_info.major}.{sys.version_info.minor} detected.",
            remediation=None if python_supported else "Install OSCA with Python 3.13.",
        )
    )
    try:
        config = load_operator_config(root)
        storage_root = Path(config.storage_root)
        checks.append(
            CompatibilityCheck(
                check_id="operator-config",
                status="pass",
                message="Versioned operator configuration is compatible.",
            )
        )
    except ValueError as exc:
        storage_root = root / "data"
        checks.append(
            CompatibilityCheck(
                check_id="operator-config",
                status="fail",
                message=str(exc),
                remediation="Run osca init or restore a compatible profile backup.",
            )
        )
    checks.append(
        CompatibilityCheck(
            check_id="storage-root",
            status="pass" if storage_root.exists() else "fail",
            message=f"Storage root: {storage_root}",
            remediation=None if storage_root.exists() else "Restore or recreate the storage root.",
        )
    )
    failed = sum(check.status == "fail" for check in checks)
    warnings = sum(check.status == "warning" for check in checks)
    return {
        "family": "osca.lifecycle-compatibility.report",
        "version": "1.0.0",
        "status": "incompatible" if failed else ("warning" if warnings else "compatible"),
        "profile_root": str(root),
        "storage_root": str(storage_root),
        "checks": [check.model_dump(mode="json") for check in checks],
        "summary": {
            "passed": len(checks) - failed - warnings,
            "warnings": warnings,
            "failed": failed,
        },
        "mutation_performed": False,
    }


def create_verified_backup(profile_root: Path, output: Path) -> dict[str, object]:
    compatibility = inspect_profile(profile_root)
    if compatibility["status"] == "incompatible":
        raise ValueError("profile is incompatible; backup refused before mutation")

    root = profile_root.resolve()
    destination = output.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in root.rglob("*") if path.is_file())
    manifest_files = [
        {
            "path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in files
    ]
    manifest = {
        "family": "osca.profile-backup.manifest",
        "version": "1.0.0",
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "osca_version": package_version(),
        "profile_root": str(root),
        "files": manifest_files,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_orders_enabled": False,
    }
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, path.relative_to(root).as_posix())
            archive.writestr("backup-manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
        with zipfile.ZipFile(temporary) as archive:
            retained = json.loads(archive.read("backup-manifest.json"))
            if retained != manifest:
                raise ValueError("backup manifest verification failed")
            for item in manifest_files:
                item_path = str(item["path"])
                expected_digest = str(item["sha256"])
                digest = hashlib.sha256(archive.read(item_path)).hexdigest()
                if digest != expected_digest:
                    raise ValueError(f"backup digest verification failed: {item_path}")
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return {
        "family": "osca.profile-backup.result",
        "version": "1.0.0",
        "status": "verified",
        "profile_root": str(root),
        "backup_path": str(destination),
        "backup_sha256": _sha256(destination),
        "file_count": len(manifest_files),
        "mutation_performed": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_orders_enabled": False,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
