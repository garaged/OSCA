from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import sys
import zipfile
from collections.abc import Callable
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path, PurePosixPath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from osca.operator_experience import load_operator_config

_SUPPORTED_PLATFORMS = {("Darwin", "arm64"), ("Linux", "x86_64")}


class CompatibilityCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    check_id: str
    status: Literal["pass", "warning", "fail"]
    message: str
    remediation: str | None = None


class BackupFile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str
    size: int = Field(ge=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class BackupManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    family: Literal["osca.profile-backup.manifest"]
    version: Literal["1.0.0"]
    created_at: str
    osca_version: str
    profile_root: str
    files: list[BackupFile]
    recommendations_enabled: Literal[False]
    broker_connections_enabled: Literal[False]
    real_capital_orders_enabled: Literal[False]


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
    if destination == root or root in destination.parents:
        raise ValueError("backup output must be outside the profile root")
    destination.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(path for path in root.rglob("*") if path.is_file())
    manifest = BackupManifest(
        family="osca.profile-backup.manifest",
        version="1.0.0",
        created_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        osca_version=package_version(),
        profile_root=str(root),
        files=[
            BackupFile(
                path=path.relative_to(root).as_posix(),
                size=path.stat().st_size,
                sha256=_sha256(path),
            )
            for path in files
        ],
        recommendations_enabled=False,
        broker_connections_enabled=False,
        real_capital_orders_enabled=False,
    )
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, path.relative_to(root).as_posix())
            archive.writestr(
                "backup-manifest.json",
                json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True),
            )
        validated = validate_backup(temporary)
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
        "file_count": len(validated.files),
        "mutation_performed": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_orders_enabled": False,
    }


def validate_backup(backup: Path) -> BackupManifest:
    archive_path = backup.resolve()
    if not archive_path.is_file():
        raise ValueError(f"backup does not exist: {archive_path}")
    try:
        with zipfile.ZipFile(archive_path) as archive:
            names = set(archive.namelist())
            if "backup-manifest.json" not in names:
                raise ValueError("backup manifest is missing")
            raw_manifest = json.loads(archive.read("backup-manifest.json"))
            manifest = BackupManifest.model_validate(raw_manifest)
            expected_names = {item.path for item in manifest.files} | {"backup-manifest.json"}
            if names != expected_names:
                raise ValueError("backup contents do not match the manifest")
            for item in manifest.files:
                _validate_archive_path(item.path)
                payload = archive.read(item.path)
                if len(payload) != item.size:
                    raise ValueError(f"backup size verification failed: {item.path}")
                if hashlib.sha256(payload).hexdigest() != item.sha256:
                    raise ValueError(f"backup digest verification failed: {item.path}")
    except (zipfile.BadZipFile, json.JSONDecodeError, ValidationError) as exc:
        raise ValueError("backup is invalid or incompatible") from exc
    return manifest


def restore_verified_backup(backup: Path, destination: Path, *, replace: bool = False) -> dict[str, object]:
    manifest = validate_backup(backup)
    target = destination.resolve()
    if target.exists() and any(target.iterdir()) and not replace:
        raise ValueError("restore destination is not empty; use --replace explicitly")

    staging = target.with_name(f".{target.name}.restore-staging")
    displaced = target.with_name(f".{target.name}.restore-previous")
    shutil.rmtree(staging, ignore_errors=True)
    shutil.rmtree(displaced, ignore_errors=True)
    staging.mkdir(parents=True)
    try:
        with zipfile.ZipFile(backup.resolve()) as archive:
            for item in manifest.files:
                output = staging / PurePosixPath(item.path)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(archive.read(item.path))
        for item in manifest.files:
            restored = staging / PurePosixPath(item.path)
            if _sha256(restored) != item.sha256:
                raise ValueError(f"restored digest verification failed: {item.path}")
        if target.exists():
            target.replace(displaced)
        staging.replace(target)
        shutil.rmtree(displaced, ignore_errors=True)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        if displaced.exists() and not target.exists():
            displaced.replace(target)
        raise

    return {
        "family": "osca.profile-restore.result",
        "version": "1.0.0",
        "status": "restored",
        "backup_path": str(backup.resolve()),
        "backup_sha256": _sha256(backup.resolve()),
        "profile_root": str(target),
        "file_count": len(manifest.files),
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_orders_enabled": False,
    }


def upgrade_profile(
    profile_root: Path,
    backup: Path,
    target_version: str,
    *,
    mutation: Callable[[Path], None] | None = None,
) -> dict[str, object]:
    root = profile_root.resolve()
    backup_result = create_verified_backup(root, backup)
    before = {path.relative_to(root).as_posix(): _sha256(path) for path in root.rglob("*") if path.is_file()}
    try:
        if mutation is not None:
            mutation(root)
        lifecycle_dir = root / "lifecycle"
        lifecycle_dir.mkdir(parents=True, exist_ok=True)
        state = {
            "family": "osca.profile-lifecycle.state",
            "version": "1.0.0",
            "installed_osca_version": target_version,
            "upgraded_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "backup_path": str(backup.resolve()),
            "backup_sha256": str(backup_result["backup_sha256"]),
        }
        (lifecycle_dir / "state.json").write_text(
            json.dumps(state, indent=2, sort_keys=True), encoding="utf-8"
        )
        compatibility = inspect_profile(root)
        if compatibility["status"] == "incompatible":
            raise ValueError("post-upgrade compatibility inspection failed")
    except Exception as exc:
        restore_verified_backup(backup, root, replace=True)
        return {
            "family": "osca.profile-upgrade.result",
            "version": "1.0.0",
            "status": "recovered",
            "target_version": target_version,
            "backup_path": str(backup.resolve()),
            "failure": str(exc),
            "pre_upgrade_digests_preserved": _profile_digests(root) == before,
            "recommendations_enabled": False,
            "broker_connections_enabled": False,
            "real_capital_orders_enabled": False,
        }

    return {
        "family": "osca.profile-upgrade.result",
        "version": "1.0.0",
        "status": "upgraded",
        "target_version": target_version,
        "backup_path": str(backup.resolve()),
        "backup_sha256": str(backup_result["backup_sha256"]),
        "pre_upgrade_file_count": len(before),
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_orders_enabled": False,
    }


def _validate_archive_path(value: str) -> None:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value in {"", "."}:
        raise ValueError(f"unsafe backup member path: {value}")


def _profile_digests(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in root.rglob("*")
        if path.is_file()
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
