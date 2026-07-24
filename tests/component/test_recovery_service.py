import shutil
import sqlite3
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from osca.catalog.api import (
    CatalogRecoveryReference,
    MetadataAvailability,
    RecoveryRecordKind,
)
from osca.configuration.api import DeploymentMode, ListenerConfiguration, SecurityConfiguration
from osca.configuration.api.contracts import ValidatedConfiguration
from osca.operations.api import AuditRecord
from osca.recovery.api import CreateBackup, ExecuteRestore, PreviewRestore, VerifyBackup
from osca.recovery.application.service import RecoveryAuthorizationDenied, RecoveryService
from osca.recovery.domain import RecoveryAction, RecoveryOperation
from osca.recovery.infrastructure.package import RecoveryPackageError, file_digest
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

    def register_recovery(
        self,
        *,
        kind: RecoveryRecordKind,
        subject_id: UUID,
        correlation_id: CorrelationId,
        producer_build: str,
        source_schema: str,
        configuration_revision: UUID,
        lineage: tuple[UUID, ...],
        availability: MetadataAvailability,
    ) -> CatalogRecoveryReference:
        self.kinds.append(kind)
        return CatalogRecoveryReference(
            kind=kind,
            subject_id=subject_id,
            correlation_id=correlation_id,
            producer_build=producer_build,
            source_schema=source_schema,
            configuration_revision=configuration_revision,
            lineage=lineage,
            availability=availability,
        )


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


class RecordingConfiguration:
    def __init__(self) -> None:
        self.snapshots: dict[UUID, ValidatedConfiguration] = {}

    def add(self, configuration: ValidatedConfiguration) -> None:
        self.snapshots[configuration.revision_id] = configuration

    def get(self, revision_id: UUID) -> ValidatedConfiguration | None:
        return self.snapshots.get(revision_id)


def _authorization(*capabilities: Capability) -> AuthorizationContext:
    return AuthorizationContext(
        actor="local-owner",
        authentication_method="operating-system-user-boundary",
        capabilities=frozenset(capabilities),
    )


def _configuration(revision: UUID) -> ValidatedConfiguration:
    return ValidatedConfiguration(
        revision_id=revision,
        profile="local",
        deployment_mode=DeploymentMode.LOCAL,
        listener=ListenerConfiguration(),
        security=SecurityConfiguration(),
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
        connection.execute(
            "CREATE TABLE configuration_snapshots (revision_id TEXT PRIMARY KEY, payload TEXT)"
        )
        connection.execute("INSERT INTO retained VALUES ('evidence')")
        connection.commit()
    finally:
        connection.close()


def _persist_configuration_row(
    database: Path, configuration: ValidatedConfiguration
) -> None:
    connection = sqlite3.connect(database)
    try:
        connection.execute(
            "INSERT INTO configuration_snapshots VALUES (?, ?)",
            (str(configuration.revision_id), configuration.model_dump_json()),
        )
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
    catalog = RecordingCatalog()
    audit = RecordingAudit()
    configurations = RecordingConfiguration()
    service = RecoveryService(
        container=CopyContainer(),
        vault=MemoryVault(),
        catalog=catalog,
        audit=audit,
        operations=RecordingOperations(),
        configuration=configurations,
        source_database=database,
    )
    correlation = CorrelationId.new()
    configuration_revision = uuid4()
    configuration = _configuration(configuration_revision)
    configurations.add(configuration)
    _persist_configuration_row(database, configuration)
    active_before = file_digest(database)
    created = service.create(
        CreateBackup(
            authorization=_authorization(Capability.RECOVERY_BACKUP),
            correlation_id=correlation,
            destination=str(package),
            recipient="age1" + "q" * 58,
            recipient_fingerprint="sha256:" + "a" * 64,
            configuration_snapshot=configuration,
            configuration_revision=configuration_revision,
            source_build="test-build",
            source_schema="m1_0005",
        )
    )
    assert b"AGE-SECRET-KEY-TEST" not in package.read_bytes()
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


def test_preview_conflict_and_package_change_block_execution(tmp_path: Path) -> None:
    database = tmp_path / "active.db"
    package = tmp_path / "backup.age"
    destination = tmp_path / "existing"
    destination.mkdir()
    _database(database)
    configurations = RecordingConfiguration()
    service = RecoveryService(
        container=CopyContainer(),
        vault=MemoryVault(),
        catalog=RecordingCatalog(),
        audit=RecordingAudit(),
        operations=RecordingOperations(),
        configuration=configurations,
        source_database=database,
    )
    correlation = CorrelationId.new()
    revision = uuid4()
    configuration = _configuration(revision)
    configurations.add(configuration)
    _persist_configuration_row(database, configuration)
    service.create(
        CreateBackup(
            authorization=_authorization(Capability.RECOVERY_BACKUP),
            correlation_id=correlation,
            destination=str(package),
            recipient="age1" + "q" * 58,
            recipient_fingerprint="sha256:" + "a" * 64,
            configuration_snapshot=configuration,
            configuration_revision=revision,
            source_build="test",
            source_schema="m1_0005",
        )
    )
    identity = SecretReference(namespace="recovery", name="age-identity")
    plan = service.preview(
        PreviewRestore(
            authorization=_authorization(Capability.RECOVERY_VERIFY),
            correlation_id=correlation,
            package=str(package),
            identity_reference=identity,
            destination=str(destination),
        )
    )
    assert not plan.executable
    executable_plan = service.preview(
        PreviewRestore(
            authorization=_authorization(Capability.RECOVERY_VERIFY),
            correlation_id=correlation,
            package=str(package),
            identity_reference=identity,
            destination=str(tmp_path / "new-destination"),
        )
    )
    assert executable_plan.executable
    package.write_bytes(package.read_bytes() + b"changed")
    with pytest.raises(RecoveryPackageError, match="package_changed"):
        service.execute(
            ExecuteRestore(
                authorization=_authorization(Capability.RECOVERY_RESTORE),
                correlation_id=correlation,
                package=str(package),
                identity_reference=identity,
                plan=executable_plan,
            )
        )


def test_missing_capability_fails_before_backup_creation(tmp_path: Path) -> None:
    service = RecoveryService(
        container=CopyContainer(),
        vault=MemoryVault(),
        catalog=RecordingCatalog(),
        audit=RecordingAudit(),
        operations=RecordingOperations(),
        configuration=RecordingConfiguration(),
        source_database=tmp_path / "missing",
    )
    with pytest.raises(RecoveryAuthorizationDenied):
        service.create(
            CreateBackup(
                authorization=_authorization(),
                correlation_id=CorrelationId.new(),
                destination=str(tmp_path / "backup.age"),
                recipient="age1" + "q" * 58,
                recipient_fingerprint="fingerprint",
                configuration_snapshot=_configuration(uuid4()),
                configuration_revision=uuid4(),
                source_build="test",
                source_schema="m1_0005",
            )
        )
    assert not (tmp_path / "backup.age").exists()
