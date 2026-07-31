from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from osca.extensions.api import ExtensionPermission, ExtensionTrustTier
from osca.runtime_extensions.contracts import (
    RuntimeExtensionStatus,
    RuntimePackEvidence,
    RuntimePackManifest,
    RuntimePackRequest,
    RuntimePackRollbackEvidence,
)

OSCA_RUNTIME_VERSION = "0.1.0"
_ALLOWED_TRUST = {
    ExtensionTrustTier.BUILT_IN,
    ExtensionTrustTier.VERIFIED,
    ExtensionTrustTier.LOCAL_TRUSTED,
}


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _version_tuple(value: str) -> tuple[int, int, int]:
    core = value.split("+", 1)[0].split("-", 1)[0]
    major, minor, patch = core.split(".")
    return int(major), int(minor), int(patch)


def _load_manifest(pack_directory: Path) -> tuple[RuntimePackManifest, Path, str]:
    manifest_path = pack_directory / "osca-pack.json"
    if not manifest_path.is_file():
        raise ValueError("pack requires osca-pack.json")
    manifest = RuntimePackManifest.model_validate_json(manifest_path.read_text())
    executable = (pack_directory / manifest.executable).resolve()
    root = pack_directory.resolve()
    if executable.parent != root or not executable.is_file():
        raise ValueError("pack executable must be a regular file directly inside the pack")
    actual_digest = _sha256(executable.read_bytes())
    if actual_digest != manifest.integrity_digest:
        raise ValueError("pack executable digest does not match manifest")
    return manifest, executable, actual_digest


def _permission_keys(
    permissions: tuple[ExtensionPermission, ...],
) -> set[tuple[str, str]]:
    return {(permission.kind.value, permission.scope) for permission in permissions}


def validate_runtime_pack(request: RuntimePackRequest) -> RuntimePackEvidence:
    pack_directory = Path(request.pack_directory).resolve()
    try:
        manifest, _executable, digest = _load_manifest(pack_directory)
    except (OSError, ValueError) as exc:
        return RuntimePackEvidence(
            package_id="invalid-pack",
            package_version="0.0.0",
            status=RuntimeExtensionStatus.FAILED,
            manifest_digest="sha256:" + "0" * 64,
            rationale=str(exc),
            findings=("pack-validation-failed",),
        )
    findings: list[str] = []
    status = RuntimeExtensionStatus.VALIDATED
    if manifest.trust_tier not in _ALLOWED_TRUST:
        status = RuntimeExtensionStatus.POLICY_BLOCKED
        findings.append("untrusted-pack")
    if _version_tuple(OSCA_RUNTIME_VERSION) < _version_tuple(manifest.osca_min_version):
        status = RuntimeExtensionStatus.INCOMPATIBLE
        findings.append("osca-version-incompatible")
    requested = _permission_keys(manifest.permissions)
    approved = _permission_keys(request.approved_permissions)
    if requested != approved:
        status = RuntimeExtensionStatus.POLICY_BLOCKED
        findings.append("permission-approval-required")
    rationale = (
        "pack validated for trusted local runtime"
        if status is RuntimeExtensionStatus.VALIDATED
        else "pack cannot execute until all trust, compatibility, and permission gates pass"
    )
    return RuntimePackEvidence(
        package_id=manifest.package_id,
        package_version=manifest.package_version,
        status=status,
        manifest_digest=digest,
        approved_permissions=request.approved_permissions,
        rationale=rationale,
        findings=tuple(findings),
    )


def install_runtime_pack(request: RuntimePackRequest) -> RuntimePackEvidence:
    validation = validate_runtime_pack(request)
    if validation.status is not RuntimeExtensionStatus.VALIDATED:
        return validation
    source = Path(request.pack_directory).resolve()
    destination = (
        Path(request.storage_root).resolve()
        / "runtime-extensions"
        / validation.package_id
        / validation.package_version
    )
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    pointer = destination.parent / "active.json"
    pointer.write_text(
        json.dumps(
            {"package_id": validation.package_id, "version": validation.package_version},
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    return validation.model_copy(
        update={
            "status": RuntimeExtensionStatus.INSTALLED,
            "rationale": "trusted pack installed and activated by explicit local operator action",
        }
    )


def execute_runtime_pack(request: RuntimePackRequest) -> RuntimePackEvidence:
    validation = validate_runtime_pack(request)
    if validation.status is not RuntimeExtensionStatus.VALIDATED:
        return validation
    if not request.enable_execution:
        return validation.model_copy(
            update={
                "status": RuntimeExtensionStatus.POLICY_BLOCKED,
                "rationale": "runtime pack execution requires explicit enablement",
                "findings": (*validation.findings, "execution-disabled"),
            }
        )
    pack_directory = Path(request.pack_directory).resolve()
    manifest, executable, digest = _load_manifest(pack_directory)
    evidence_root = (
        Path(request.storage_root).resolve()
        / "runtime-extensions"
        / manifest.package_id
        / "evidence"
        / str(validation.evidence_id)
    )
    evidence_root.mkdir(parents=True, exist_ok=False)
    stdout_path = evidence_root / "stdout.json"
    stderr_path = evidence_root / "stderr.txt"
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONIOENCODING": "utf-8",
        "OSCA_EXTENSION_NETWORK": "disabled",
        "OSCA_EXTENSION_SECRETS": "disabled",
    }
    command = [str(executable), *manifest.arguments]
    try:
        completed = subprocess.run(
            command,
            cwd=pack_directory,
            input=request.input_payload,
            text=True,
            capture_output=True,
            timeout=manifest.max_runtime_seconds,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        stderr_path.write_text(str(exc))
        return validation.model_copy(
            update={
                "status": RuntimeExtensionStatus.FAILED,
                "stderr_uri": str(stderr_path),
                "rationale": "runtime pack exceeded its declared timeout",
                "findings": (*validation.findings, "runtime-timeout"),
            }
        )
    stdout_bytes = completed.stdout.encode()
    stderr_bytes = completed.stderr.encode()
    if len(stdout_bytes) + len(stderr_bytes) > manifest.max_output_bytes:
        return validation.model_copy(
            update={
                "status": RuntimeExtensionStatus.FAILED,
                "exit_code": completed.returncode,
                "rationale": "runtime pack output exceeded its declared byte budget",
                "findings": (*validation.findings, "output-budget-exceeded"),
            }
        )
    try:
        output: Any = json.loads(completed.stdout)
    except json.JSONDecodeError:
        output = None
    stdout_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    stderr_path.write_text(completed.stderr)
    status = (
        RuntimeExtensionStatus.SUCCEEDED
        if completed.returncode == 0 and isinstance(output, dict)
        else RuntimeExtensionStatus.FAILED
    )
    findings = list(validation.findings)
    if completed.returncode != 0:
        findings.append("nonzero-exit")
    if not isinstance(output, dict):
        findings.append("invalid-json-object-output")
    return RuntimePackEvidence(
        evidence_id=validation.evidence_id,
        package_id=manifest.package_id,
        package_version=manifest.package_version,
        status=status,
        manifest_digest=digest,
        approved_permissions=request.approved_permissions,
        stdout_uri=str(stdout_path),
        stderr_uri=str(stderr_path),
        output_digest=_sha256(stdout_path.read_bytes()),
        exit_code=completed.returncode,
        rationale=(
            "trusted runtime pack completed with retained evidence"
            if status is RuntimeExtensionStatus.SUCCEEDED
            else "runtime pack failed contract or process validation"
        ),
        findings=tuple(findings),
    )


def rollback_runtime_pack(
    *, storage_root: str, package_id: str, target_version: str
) -> RuntimePackRollbackEvidence:
    package_root = Path(storage_root).resolve() / "runtime-extensions" / package_id
    pointer = package_root / "active.json"
    if not pointer.is_file():
        raise ValueError("active extension pointer does not exist")
    current = json.loads(pointer.read_text())
    target = package_root / target_version
    if not target.is_dir():
        raise ValueError("target rollback version is not installed")
    target_manifest, _executable, _digest = _load_manifest(target)
    if target_manifest.package_id != package_id:
        raise ValueError("rollback target package identity does not match")
    pointer.write_text(
        json.dumps({"package_id": package_id, "version": target_version}, indent=2)
        + "\n"
    )
    return RuntimePackRollbackEvidence(
        package_id=package_id,
        from_version=str(current["version"]),
        to_version=target_version,
        status=RuntimeExtensionStatus.ROLLED_BACK,
        active_pointer_uri=str(pointer),
        rationale="active pack pointer rolled back to an already validated installed version",
    )
