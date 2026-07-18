from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.recovery.api import BackupManifest, ManifestEntry, RestorePlan


def _entry(path: str) -> ManifestEntry:
    return ManifestEntry(
        path=path,
        size=1,
        digest="sha256:" + "a" * 64,
        media_type="application/octet-stream",
    )


def _manifest() -> BackupManifest:
    return BackupManifest(
        source_build="test-build",
        source_schema="m1_0004",
        configuration_revision=uuid4(),
        recipient_fingerprints=("sha256:" + "b" * 64,),
        entries=(
            _entry("state/osca.db"),
            _entry("configuration/snapshot.json"),
            _entry("exclusions.json"),
        ),
        exclusions=("secret-values", "sqlite-transients"),
    )


def test_manifest_integrity_is_deterministic() -> None:
    manifest = _manifest().with_integrity()
    assert manifest.verify_integrity()
    assert manifest.with_integrity().integrity_digest == manifest.integrity_digest


@pytest.mark.parametrize(
    "path", ("/absolute", "../escape", "state/../escape", "./state/osca.db")
)
def test_manifest_rejects_unsafe_paths(path: str) -> None:
    with pytest.raises(ValidationError):
        _entry(path)


def test_manifest_rejects_duplicate_or_undeclared_entries() -> None:
    with pytest.raises(ValidationError):
        BackupManifest(
            source_build="test-build",
            source_schema="m1_0004",
            configuration_revision=uuid4(),
            recipient_fingerprints=("recipient",),
            entries=(
                _entry("state/osca.db"),
                _entry("state/osca.db"),
                _entry("exclusions.json"),
            ),
            exclusions=(),
        )


def test_restore_plan_is_immutable_and_conflicts_block_execution() -> None:
    plan = RestorePlan(
        backup_id=uuid4(),
        package_digest="sha256:" + "c" * 64,
        destination="/isolated/restore",
        operations=("create destination", "extract snapshot"),
        conflicts=("destination exists",),
        required_validations=("sqlite integrity",),
    ).with_integrity()
    assert plan.verify_integrity()
    assert not plan.executable
    with pytest.raises(ValidationError):
        plan.destination = "/active"  # type: ignore[misc]
