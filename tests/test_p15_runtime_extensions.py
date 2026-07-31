from __future__ import annotations

import hashlib
import json
import stat
from pathlib import Path

import pytest

from osca.runtime_extensions import (
    RuntimeExtensionStatus,
    RuntimePackRequest,
    execute_runtime_pack,
    install_runtime_pack,
    rollback_runtime_pack,
    validate_runtime_pack,
)


def _pack(
    root: Path,
    *,
    version: str = "1.0.0",
    trust: str = "local_trusted",
    min_version: str = "0.1.0",
    body: str = "#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps({'ok': True, 'input': json.load(sys.stdin)}))\n",
) -> Path:
    pack = root / f"pack-{version}"
    pack.mkdir()
    executable = pack / "run.py"
    executable.write_text(body)
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    digest = "sha256:" + hashlib.sha256(executable.read_bytes()).hexdigest()
    (pack / "osca-pack.json").write_text(
        json.dumps(
            {
                "package_id": "example-pack",
                "package_version": version,
                "publisher": "example",
                "category": "analysis",
                "executable": "run.py",
                "osca_min_version": min_version,
                "trust_tier": trust,
                "integrity_digest": digest,
                "permissions": [],
                "max_runtime_seconds": 5,
                "max_output_bytes": 10000,
            }
        )
    )
    return pack


def test_trusted_pack_validates(tmp_path: Path) -> None:
    evidence = validate_runtime_pack(RuntimePackRequest(pack_directory=str(_pack(tmp_path))))
    assert evidence.status is RuntimeExtensionStatus.VALIDATED


def test_untrusted_pack_is_policy_blocked(tmp_path: Path) -> None:
    evidence = validate_runtime_pack(
        RuntimePackRequest(pack_directory=str(_pack(tmp_path, trust="untrusted")))
    )
    assert evidence.status is RuntimeExtensionStatus.POLICY_BLOCKED
    assert "untrusted-pack" in evidence.findings


def test_incompatible_pack_fails_closed(tmp_path: Path) -> None:
    evidence = validate_runtime_pack(
        RuntimePackRequest(pack_directory=str(_pack(tmp_path, min_version="9.0.0")))
    )
    assert evidence.status is RuntimeExtensionStatus.INCOMPATIBLE


def test_digest_mismatch_fails_validation(tmp_path: Path) -> None:
    pack = _pack(tmp_path)
    (pack / "run.py").write_text("tampered")
    evidence = validate_runtime_pack(RuntimePackRequest(pack_directory=str(pack)))
    assert evidence.status is RuntimeExtensionStatus.FAILED


def test_execution_requires_explicit_enablement(tmp_path: Path) -> None:
    evidence = execute_runtime_pack(RuntimePackRequest(pack_directory=str(_pack(tmp_path))))
    assert evidence.status is RuntimeExtensionStatus.POLICY_BLOCKED
    assert "execution-disabled" in evidence.findings


def test_trusted_pack_executes_and_retains_evidence(tmp_path: Path) -> None:
    evidence = execute_runtime_pack(
        RuntimePackRequest(
            pack_directory=str(_pack(tmp_path)),
            storage_root=str(tmp_path / "storage"),
            enable_execution=True,
            input_payload='{"symbol":"AAPL"}',
        )
    )
    assert evidence.status is RuntimeExtensionStatus.SUCCEEDED
    assert evidence.exit_code == 0
    assert evidence.stdout_uri is not None
    assert Path(evidence.stdout_uri).is_file()


def test_install_and_rollback_use_existing_validated_versions(tmp_path: Path) -> None:
    storage = tmp_path / "storage"
    first = install_runtime_pack(
        RuntimePackRequest(pack_directory=str(_pack(tmp_path, version="1.0.0")), storage_root=str(storage))
    )
    second = install_runtime_pack(
        RuntimePackRequest(pack_directory=str(_pack(tmp_path, version="2.0.0")), storage_root=str(storage))
    )
    assert first.status is RuntimeExtensionStatus.INSTALLED
    assert second.status is RuntimeExtensionStatus.INSTALLED
    rollback = rollback_runtime_pack(
        storage_root=str(storage), package_id="example-pack", target_version="1.0.0"
    )
    assert rollback.status is RuntimeExtensionStatus.ROLLED_BACK
    assert rollback.from_version == "2.0.0"


def test_rollback_rejects_missing_version(tmp_path: Path) -> None:
    storage = tmp_path / "storage"
    install_runtime_pack(
        RuntimePackRequest(pack_directory=str(_pack(tmp_path)), storage_root=str(storage))
    )
    with pytest.raises(ValueError, match="not installed"):
        rollback_runtime_pack(
            storage_root=str(storage), package_id="example-pack", target_version="9.0.0"
        )
