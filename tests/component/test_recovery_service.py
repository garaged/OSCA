import shutil
import sqlite3
from pathlib import Path
from uuid import uuid4

import pytest

from osca.operations.api import AuditRecord
from osca.recovery.api import CreateBackup, ExecuteRestore, PreviewRestore, VerifyBackup
from osca.recovery.application.service import RecoveryAuthorizationDenied, RecoveryService
from osca.recovery.domain import RecoveryAction, RecoveryOperation
from osca.recovery.infrastructure.package import file_digest
from osca.security.api import AuthorizationContext, Capability, SecretReference
from osca.shared_kernel.api import CorrelationId


class CopyContainer:
    container_id = "age/v1+x25519"

    def encrypt(self, cleartext: Path, destination: Path, recipient: str) -> None:
        shutil.copyfile(cleartext, destination)

    def decrypt(self, package: Path, cleartext: Path, identity: bytes) -> None:
        assert identity == b"AGE-SECRET-KEY-TEST"
        shutil.copyfile(package, cleartext)


class MemoryVault:
    def store(self, reference: SecretReference, value: str) -> None:
        pass

    def resolve(self, reference: SecretReference) -> str | None:
        return "AGE-SECRET-KEY-TEST"

    def delete(self, reference: SecretReference) -> bool:
        return True


class RecordingCatalog:
    def __init__(self) -> None:
        self.kinds: list[object] = []

    def register_recovery(self, **values: object) -> object:
        self.kinds.append(values["kind"])
        return object()


class RecordingAudit:
    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def add(self, record: AuditRecord) -> None:
        self.records.append(record)

    def get(self, record_id: object) -> AuditRecord | None:
        return None


class RecordingOperations:
    def __init__(self) -> None:
        self.completed: list[bool] = []

    def start(
        self,
        *,
        correlation_id: CorrelationId,
        actor: str,
        action: RecoveryAction,
        target: str,
    ) -> RecoveryOperation:
        return RecoveryOperation(
            correlation_id=correlation_id,
            actor=actor,
            action=action,
            target=target,
        )

    def complete(
        self, operation: RecoveryOperation, *, succeeded: bool, code: str
    ) -> RecoveryOperation:
        self.completed.append(succeeded)
        return operation


def _authorization(*capabilities: Capability) -> AuthorizationContext:
    return AuthorizationContext(
        actor="local-owner",
        authentication_method="operating-system-user-boundary",
        capabilities=frozenset(capabilities),
    )


def _database(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE retained (value TEXT NOT NULL)")
        connection.execute("CREATE TABLE alembic_version (version_num TEXT NOT NULL)")
        connection.execute("INSERT INTO alembic_version VALUES ('m1_0005')")
        connection.execute("CREATE TABLE catalog_result_metadata (result_id TEXT)")
        connection.execute("CREATE TABLE catalog_recovery_metadata (record_id TEXT)")
        connection.execute("CREATE TABLE operations_audit_records (record_id TEXT)")
        connection.execute("INSERT INTO retained VALUES ('evidence')")
        connection.commit()
    finally:
        connection.close()


def test_create_verify_preview_and_isolated_restore_leave_active_unchanged(
    tmp_path: Path,
) -> None:
    database = tmp_path / "active.db"
    package = tmp_path / "backup.age"
    restored = tmp_path / "isolated"
    _database(database)
    active_before = file_digest(database)
    catalog = RecordingCatalog()
    audit = RecordingAudit()
    service = RecoveryService(
        container=CopyContainer(),
        vault=MemoryVault(),
        catalog=catalog,
        audit=audit,
        operations=RecordingOperations(),
    )
    correlation = CorrelationId.new()
    configuration_revision = uuid4()
    created = service.create(
        CreateBackup(
            authorization=_authorization(Capability.RECOVERY_BACKUP),
            correlation_id=correlation,
            source_database=str(database),
            destination=str(package),
            recipient="age1" + "q" * 58,
            recipient_fingerprint="sha256:" + "a" * 64,
            configuration_snapshot={"profile": "local", "identity": "vault://recovery/key"},
            configuration_revision=configuration_revision,
            source_build="test-build",
            source_schema="m1_0005",
        )
    )
    identity = SecretReference(namespace="recovery", name="age-identity")
    manifest, _ = service.verify(
        VerifyBackup(
            authorization=_authorization(Capability.RECOVERY_VERIFY),
            correlation_id=correlation,
            package=str(package),
            identity_reference=identity,
        )
    )
    assert manifest.backup_id == created.backup_id
    plan = service.preview(
        PreviewRestore(
            authorization=_authorization(Capability.RECOVERY_VERIFY),
            correlation_id=correlation,
            package=str(package),
            identity_reference=identity,
            destination=str(restored),
        )
    )
    record = service.execute(
        ExecuteRestore(
            authorization=_authorization(Capability.RECOVERY_RESTORE),
            correlation_id=correlation,
            package=str(package),
            identity_reference=identity,
            plan=plan,
        )
    )
    assert all(validation.passed for validation in record.validations)
    assert len(record.validations) == 5
    assert (restored / "state/osca.db").is_file()
    assert file_digest(database) == active_before
    assert len(catalog.kinds) == 2
    assert [item.action for item in audit.records] == ["backup.create", "restore.execute"]


def test_missing_capability_fails_before_backup_creation(tmp_path: Path) -> None:
    service = RecoveryService(
        container=CopyContainer(),
        vault=MemoryVault(),
        catalog=RecordingCatalog(),
        audit=RecordingAudit(),
        operations=RecordingOperations(),
    )
    with pytest.raises(RecoveryAuthorizationDenied):
        service.create(
            CreateBackup(
                authorization=_authorization(),
                correlation_id=CorrelationId.new(),
                source_database=str(tmp_path / "missing"),
                destination=str(tmp_path / "backup.age"),
                recipient="age1" + "q" * 58,
                recipient_fingerprint="fingerprint",
                configuration_snapshot={},
                configuration_revision=uuid4(),
                source_build="test",
                source_schema="m1_0005",
            )
        )
    assert not (tmp_path / "backup.age").exists()
