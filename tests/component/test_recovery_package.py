import sqlite3
import zipfile
from pathlib import Path
from uuid import uuid4

import pytest

from osca.recovery.infrastructure.package import (
    RecoveryPackageError,
    build_cleartext_package,
    validate_cleartext_package,
)


def _source_database(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE evidence (value TEXT NOT NULL)")
        connection.execute("INSERT INTO evidence VALUES ('retained')")
        connection.commit()
    finally:
        connection.close()


def test_build_and_validate_consistent_package(tmp_path: Path) -> None:
    source = tmp_path / "source.db"
    package = tmp_path / "backup.fixture.zip"
    _source_database(source)
    expected = build_cleartext_package(
        source_database=source,
        destination=package,
        configuration_snapshot={"profile": "local", "secret_reference": "vault:test"},
        configuration_revision=uuid4(),
        source_build="test-build",
        source_schema="m1_0004",
        recipient_fingerprints=("sha256:" + "a" * 64,),
    )
    actual = validate_cleartext_package(package)
    assert actual == expected
    with zipfile.ZipFile(package) as archive:
        assert "retained" in archive.read("state/osca.db").decode(errors="ignore")
        assert "secret_reference" in archive.read("configuration/snapshot.json").decode()


def test_tampered_payload_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "source.db"
    package = tmp_path / "backup.fixture.zip"
    _source_database(source)
    build_cleartext_package(
        source_database=source,
        destination=package,
        configuration_snapshot={"profile": "local"},
        configuration_revision=uuid4(),
        source_build="test-build",
        source_schema="m1_0004",
        recipient_fingerprints=("recipient",),
    )
    with zipfile.ZipFile(package, "a") as archive:
        archive.writestr("state/osca.db", b"tampered")
    with pytest.raises(RecoveryPackageError, match="entries_invalid"):
        validate_cleartext_package(package)


def test_traversal_entry_is_rejected(tmp_path: Path) -> None:
    package = tmp_path / "malicious.zip"
    with zipfile.ZipFile(package, "w") as archive:
        archive.writestr("../escape", b"unsafe")
    with pytest.raises(RecoveryPackageError, match="entries_invalid"):
        validate_cleartext_package(package)


def test_incompatible_schema_is_rejected_before_restore(tmp_path: Path) -> None:
    source = tmp_path / "source.db"
    package = tmp_path / "future.fixture.zip"
    _source_database(source)
    build_cleartext_package(
        source_database=source,
        destination=package,
        configuration_snapshot={"profile": "local"},
        configuration_revision=uuid4(),
        source_build="future",
        source_schema="m9_0001",
        recipient_fingerprints=("recipient",),
    )
    with pytest.raises(RecoveryPackageError, match="schema_incompatible"):
        validate_cleartext_package(package)
