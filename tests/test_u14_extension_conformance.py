from __future__ import annotations

import hashlib
import json
from pathlib import Path

from osca.extension_conformance import validate_extension_package


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_manifest(root: Path, **overrides: object) -> Path:
    artifact = root / "extension.py"
    artifact.write_text("VALUE = 1\n", encoding="utf-8")
    document: dict[str, object] = {
        "family": "osca.extension-manifest",
        "manifest_version": "1.0.0",
        "extension_id": "example.offline-metric",
        "extension_version": "0.1.0",
        "api_version": "1.0",
        "entry_point": "extension:compute",
        "trust": "trusted-local",
        "license_spdx": "Apache-2.0",
        "source_repository": "https://example.invalid/osca-extension",
        "source_commit": "a" * 40,
        "capabilities": ["dataset.read", "metrics.compute"],
        "artifacts": [{"path": "extension.py", "sha256": _digest(artifact)}],
        "network_access": False,
        "remote_installation": False,
        "automatic_updates": False,
    }
    document.update(overrides)
    manifest = root / "osca-extension.json"
    manifest.write_text(json.dumps(document), encoding="utf-8")
    return manifest


def test_validates_trusted_local_package_without_importing_code(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path)

    result = validate_extension_package(manifest)

    assert result.status == "valid"
    assert result.extension_id == "example.offline-metric"
    assert result.verified_artifacts == ("extension.py",)
    assert result.code_imported is False
    assert result.execution_enabled is False


def test_rejects_forbidden_capability(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path, capabilities=["dataset.read", "exchange.order"])

    result = validate_extension_package(manifest)

    assert result.status == "invalid"
    assert "forbidden capabilities" in " ".join(result.errors)


def test_rejects_unknown_capability(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path, capabilities=["dataset.read", "filesystem.root"])

    result = validate_extension_package(manifest)

    assert result.status == "invalid"
    assert "unknown capabilities" in " ".join(result.errors)


def test_rejects_artifact_digest_mismatch(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path)
    (tmp_path / "extension.py").write_text("VALUE = 2\n", encoding="utf-8")

    result = validate_extension_package(manifest)

    assert result.status == "invalid"
    assert result.errors == ("artifact digest mismatch: extension.py",)


def test_rejects_path_traversal_before_reading_artifact(tmp_path: Path) -> None:
    manifest = _write_manifest(
        tmp_path,
        artifacts=[{"path": "../outside.py", "sha256": "0" * 64}],
    )

    result = validate_extension_package(manifest)

    assert result.status == "invalid"
    assert "contained relative path" in " ".join(result.errors)


def test_rejects_remote_or_automatic_installation_flags(tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path, remote_installation=True, automatic_updates=True)

    result = validate_extension_package(manifest)

    assert result.status == "invalid"
    assert result.code_imported is False
