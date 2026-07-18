from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import stat
import zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from uuid import UUID

from osca.recovery.api import BackupManifest, ManifestEntry
from osca.recovery.application.ports import EncryptionContainer

_MANIFEST_PATH = "manifest.json"
_ALLOWED_PAYLOADS = {
    "state/osca.db": "application/vnd.sqlite3",
    "configuration/snapshot.json": "application/json",
    "exclusions.json": "application/json",
}
_MAX_ENTRY_BYTES = 256 * 1024 * 1024
_MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
_READABLE_SCHEMAS = {f"m1_{revision:04d}" for revision in range(1, 7)}


class RecoveryPackageError(RuntimeError):
    """Stable safe package-validation failure."""


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def _bytes_digest(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def create_sqlite_snapshot(source: Path, destination: Path) -> None:
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    source_connection = sqlite3.connect(f"file:{source.resolve()}?mode=ro", uri=True)
    destination_connection = sqlite3.connect(destination)
    try:
        source_connection.backup(destination_connection)
    finally:
        destination_connection.close()
        source_connection.close()
    os.chmod(destination, 0o600)


def _zip_info(path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, _ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = (stat.S_IFREG | 0o600) << 16
    return info


def _canonical_json(payload: object) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def build_cleartext_package(
    *,
    source_database: Path,
    destination: Path,
    configuration_snapshot: Mapping[str, object],
    configuration_revision: UUID,
    source_build: str,
    source_schema: str,
    recipient_fingerprints: Sequence[str],
) -> BackupManifest:
    """Build a deterministic plaintext fixture; never expose this as a production command."""

    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    exclusions = ("secret-values", "sqlite-wal", "sqlite-shm", "runtime-transients")
    with TemporaryDirectory(dir=destination.parent, prefix=".osca-recovery-") as temporary:
        staging = Path(temporary)
        database = staging / "osca.db"
        create_sqlite_snapshot(source_database, database)
        payloads = {
            "state/osca.db": database.read_bytes(),
            "configuration/snapshot.json": _canonical_json(configuration_snapshot),
            "exclusions.json": _canonical_json({"excluded": exclusions}),
        }
        entries = tuple(
            ManifestEntry(
                path=path,
                size=len(content),
                digest=_bytes_digest(content),
                media_type=_ALLOWED_PAYLOADS[path],
            )
            for path, content in sorted(payloads.items())
        )
        manifest = BackupManifest(
            source_build=source_build,
            source_schema=source_schema,
            configuration_revision=configuration_revision,
            recipient_fingerprints=tuple(recipient_fingerprints),
            entries=entries,
            exclusions=exclusions,
        ).with_integrity()
        temporary_package = staging / "package.zip"
        with zipfile.ZipFile(temporary_package, "w") as archive:
            archive.writestr(_zip_info(_MANIFEST_PATH), manifest.model_dump_json())
            for path, content in sorted(payloads.items()):
                archive.writestr(_zip_info(path), content)
        os.chmod(temporary_package, 0o600)
        os.replace(temporary_package, destination)
    return manifest


def create_protected_package(
    *,
    container: EncryptionContainer,
    cleartext_package: Path,
    destination: Path,
    recipient: str,
) -> str:
    if container.container_id != "age/v1+x25519":
        raise RecoveryPackageError("recovery.container.unsupported")
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with TemporaryDirectory(dir=destination.parent, prefix=".osca-encryption-") as temporary:
        encrypted = Path(temporary) / "package.age"
        container.encrypt(cleartext_package, encrypted, recipient)
        if not encrypted.is_file():
            raise RecoveryPackageError("recovery.encryption.no_output")
        os.chmod(encrypted, 0o600)
        digest = file_digest(encrypted)
        os.replace(encrypted, destination)
    return digest


def validate_cleartext_package(package: Path) -> BackupManifest:
    if package.stat().st_size > _MAX_ARCHIVE_BYTES:
        raise RecoveryPackageError("recovery.package.too_large")
    try:
        with zipfile.ZipFile(package) as archive:
            infos = archive.infolist()
            if sum(info.file_size for info in infos) > _MAX_ARCHIVE_BYTES:
                raise RecoveryPackageError("recovery.package.expanded_size_too_large")
            paths = [info.filename for info in infos]
            expected = {_MANIFEST_PATH, *_ALLOWED_PAYLOADS}
            if len(paths) != len(set(paths)) or set(paths) != expected:
                raise RecoveryPackageError("recovery.package.entries_invalid")
            for info in infos:
                path = PurePosixPath(info.filename)
                if path.is_absolute() or ".." in path.parts or info.is_dir():
                    raise RecoveryPackageError("recovery.package.path_unsafe")
                if info.file_size > _MAX_ENTRY_BYTES:
                    raise RecoveryPackageError("recovery.package.entry_too_large")
                unix_mode = info.external_attr >> 16
                if unix_mode and not stat.S_ISREG(unix_mode):
                    raise RecoveryPackageError("recovery.package.entry_type_invalid")
            manifest = BackupManifest.model_validate_json(archive.read(_MANIFEST_PATH))
            if not manifest.verify_integrity():
                raise RecoveryPackageError("recovery.manifest.integrity_invalid")
            if manifest.source_schema not in _READABLE_SCHEMAS:
                raise RecoveryPackageError("recovery.manifest.schema_incompatible")
            for entry in manifest.entries:
                content = archive.read(entry.path)
                if len(content) != entry.size or _bytes_digest(content) != entry.digest:
                    raise RecoveryPackageError("recovery.package.checksum_invalid")
            return manifest
    except (OSError, zipfile.BadZipFile, KeyError, ValueError) as error:
        if isinstance(error, RecoveryPackageError):
            raise
        raise RecoveryPackageError("recovery.package.invalid") from error
