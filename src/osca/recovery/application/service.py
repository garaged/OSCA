from __future__ import annotations

import os
import sqlite3
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from osca.catalog.api import MetadataAvailability, RecoveryRecordKind
from osca.operations.api import AuditOutcome, AuditRecord
from osca.operations.application.ports import AuditRepository
from osca.recovery.api import (
    BackupManifest,
    BackupRecord,
    CreateBackup,
    ExecuteRestore,
    PreviewRestore,
    RecoveryAvailability,
    RestorePlan,
    RestoreRecord,
    RestoreValidation,
    VerifyBackup,
)
from osca.recovery.application.ports import (
    EncryptionContainer,
    NullRecoveryObserver,
    RecoveryCatalog,
    RecoveryObserver,
    RecoveryOperationRepository,
)
from osca.recovery.domain import RecoveryAction
from osca.recovery.infrastructure.package import (
    RecoveryPackageError,
    build_cleartext_package,
    create_protected_package,
    file_digest,
    validate_cleartext_package,
)
from osca.security.api import AuthorizationContext, Capability
from osca.security.application.ports import SecretVault
from osca.shared_kernel.api import CorrelationId


class RecoveryAuthorizationDenied(PermissionError):
    pass


def _require(context: AuthorizationContext, capability: Capability) -> None:
    if capability not in context.capabilities:
        raise RecoveryAuthorizationDenied(f"missing capability: {capability.value}")


class RecoveryService:
    def __init__(
        self,
        *,
        container: EncryptionContainer,
        vault: SecretVault,
        catalog: RecoveryCatalog,
        audit: AuditRepository,
        operations: RecoveryOperationRepository,
        observer: RecoveryObserver | None = None,
    ) -> None:
        self._container = container
        self._vault = vault
        self._catalog = catalog
        self._audit = audit
        self._operations = operations
        self._observer = observer or NullRecoveryObserver()

    def create(self, command: CreateBackup) -> BackupRecord:
        _require(command.authorization, Capability.RECOVERY_BACKUP)
        with self._track(
            authorization=command.authorization,
            correlation_id=command.correlation_id,
            action=RecoveryAction.CREATE,
            target=command.destination,
        ):
            return self._create(command)

    def _create(self, command: CreateBackup) -> BackupRecord:
        destination = Path(command.destination).resolve()
        if destination.exists():
            raise RecoveryPackageError("recovery.destination.exists")
        with TemporaryDirectory(
            dir=destination.parent, prefix=".osca-cleartext-package-"
        ) as temporary:
            cleartext = Path(temporary) / "backup.fixture.zip"
            manifest = build_cleartext_package(
                source_database=Path(command.source_database),
                destination=cleartext,
                configuration_snapshot=command.configuration_snapshot.model_dump(mode="json"),
                configuration_revision=command.configuration_revision,
                source_build=command.source_build,
                source_schema=command.source_schema,
                recipient_fingerprints=(command.recipient_fingerprint,),
            )
            package_digest = create_protected_package(
                container=self._container,
                cleartext_package=cleartext,
                destination=destination,
                recipient=command.recipient,
            )
        record = BackupRecord(
            backup_id=manifest.backup_id,
            correlation_id=command.correlation_id,
            source_build=command.source_build,
            source_schema=command.source_schema,
            configuration_revision=command.configuration_revision,
            package_digest=package_digest,
            manifest_digest=manifest.integrity_digest,
        )
        self._catalog.register_recovery(
            kind=RecoveryRecordKind.BACKUP,
            subject_id=manifest.backup_id,
            correlation_id=command.correlation_id,
            producer_build=command.source_build,
            source_schema=command.source_schema,
            configuration_revision=command.configuration_revision,
            lineage=(command.configuration_revision,),
            availability=MetadataAvailability.AVAILABLE,
        )
        self._audit_success(
            command.authorization, command.correlation_id, "backup.create", manifest.backup_id
        )
        return record

    def verify(self, query: VerifyBackup) -> tuple[BackupManifest, str]:
        _require(query.authorization, Capability.RECOVERY_VERIFY)
        with self._track(
            authorization=query.authorization,
            correlation_id=query.correlation_id,
            action=RecoveryAction.VERIFY,
            target=query.package,
        ):
            return self._verify(query)

    def _verify(self, query: VerifyBackup) -> tuple[BackupManifest, str]:
        package = Path(query.package).resolve()
        active_digest = file_digest(package)
        identity = self._vault.resolve(query.identity_reference)
        if identity is None:
            raise RecoveryPackageError("recovery.identity.missing")
        with TemporaryDirectory(prefix=".osca-verify-") as temporary:
            cleartext = Path(temporary) / "package.zip"
            self._container.decrypt(package, cleartext, identity.encode())
            manifest = validate_cleartext_package(cleartext)
        if file_digest(package) != active_digest:
            raise RecoveryPackageError("recovery.package.changed_during_verification")
        return manifest, active_digest

    def preview(self, query: PreviewRestore) -> RestorePlan:
        _require(query.authorization, Capability.RECOVERY_VERIFY)
        with self._track(
            authorization=query.authorization,
            correlation_id=query.correlation_id,
            action=RecoveryAction.PREVIEW,
            target=query.destination,
        ):
            return self._preview(query)

    def _preview(self, query: PreviewRestore) -> RestorePlan:
        manifest, package_digest = self._verify(query)
        destination = Path(query.destination).resolve()
        conflicts = ("destination exists",) if destination.exists() else ()
        return RestorePlan(
            backup_id=manifest.backup_id,
            package_digest=package_digest,
            destination=str(destination),
            operations=("create isolated destination", "extract validated M1 state"),
            conflicts=conflicts,
            required_validations=(
                "sqlite integrity",
                "schema compatibility",
                "catalog references",
                "audit structure",
                "readiness smoke",
            ),
        ).with_integrity()

    def execute(self, command: ExecuteRestore) -> RestoreRecord:
        _require(command.authorization, Capability.RECOVERY_RESTORE)
        with self._track(
            authorization=command.authorization,
            correlation_id=command.correlation_id,
            action=RecoveryAction.EXECUTE,
            target=command.plan.destination,
        ):
            return self._execute(command)

    def _execute(self, command: ExecuteRestore) -> RestoreRecord:
        if not command.plan.verify_integrity() or not command.plan.executable:
            raise RecoveryPackageError("recovery.plan.not_executable")
        package = Path(command.package).resolve()
        if file_digest(package) != command.plan.package_digest:
            raise RecoveryPackageError("recovery.plan.package_changed")
        destination = Path(command.plan.destination)
        try:
            destination.mkdir(mode=0o700, parents=False, exist_ok=False)
        except FileExistsError as error:
            raise RecoveryPackageError("recovery.destination.exists") from error
        validations: list[RestoreValidation] = []
        try:
            identity = self._vault.resolve(command.identity_reference)
            if identity is None:
                raise RecoveryPackageError("recovery.identity.missing")
            cleartext = destination / ".package.zip"
            self._container.decrypt(package, cleartext, identity.encode())
            manifest = validate_cleartext_package(cleartext)
            if manifest.backup_id != command.plan.backup_id:
                raise RecoveryPackageError("recovery.plan.backup_changed")
            with zipfile.ZipFile(cleartext) as archive:
                for entry in manifest.entries:
                    target = destination / entry.path
                    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                    target.write_bytes(archive.read(entry.path))
                    os.chmod(target, 0o600)
            cleartext.unlink()
            database = destination / "state/osca.db"
            validations.extend(self._post_restore_validations(database, manifest.source_schema))
            if not all(validation.passed for validation in validations):
                raise RecoveryPackageError("recovery.restore.integrity_failed")
        except Exception:
            # The isolated destination is retained for diagnosis; active state is never touched.
            raise
        record = RestoreRecord(
            plan_id=command.plan.plan_id,
            backup_id=command.plan.backup_id,
            correlation_id=command.correlation_id,
            destination=str(destination),
            validations=tuple(validations),
            availability=RecoveryAvailability.AVAILABLE,
        )
        self._catalog.register_recovery(
            kind=RecoveryRecordKind.RESTORE,
            subject_id=record.record_id,
            correlation_id=command.correlation_id,
            producer_build="restore",
            source_schema=manifest.source_schema,
            configuration_revision=manifest.configuration_revision,
            lineage=(manifest.backup_id,),
            availability=MetadataAvailability.AVAILABLE,
        )
        self._audit_success(
            command.authorization,
            command.correlation_id,
            "restore.execute",
            record.record_id,
        )
        return record

    @contextmanager
    def _track(
        self,
        *,
        authorization: AuthorizationContext,
        correlation_id: CorrelationId,
        action: RecoveryAction,
        target: str,
    ) -> Iterator[None]:
        operation = self._operations.start(
            correlation_id=correlation_id,
            actor=authorization.actor,
            action=action,
            target=target,
        )
        try:
            yield
        except Exception:
            completed = self._operations.complete(
                operation, succeeded=False, code="recovery.operation.failed"
            )
            self._observer.record(completed)
            if action in {RecoveryAction.CREATE, RecoveryAction.EXECUTE}:
                self._audit_outcome(
                    authorization,
                    correlation_id,
                    action.value,
                    operation.operation_id,
                    AuditOutcome.FAILED,
                    "recovery.operation.failed",
                )
            raise
        else:
            completed = self._operations.complete(
                operation, succeeded=True, code="recovery.operation.succeeded"
            )
            self._observer.record(completed)

    def _post_restore_validations(
        self, database: Path, expected_schema: str
    ) -> tuple[RestoreValidation, ...]:
        connection = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
        try:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            schema_row = connection.execute(
                "SELECT version_num FROM alembic_version LIMIT 1"
            ).fetchone()
            foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
            smoke = connection.execute("SELECT 1").fetchone()
        except sqlite3.Error as error:
            raise RecoveryPackageError("recovery.restore.validation_failed") from error
        finally:
            connection.close()
        schema_ok = schema_row is not None and schema_row[0] == expected_schema
        catalog_ok = {
            "catalog_result_metadata",
            "catalog_recovery_metadata",
        }.issubset(tables) and not foreign_keys
        audit_ok = "operations_audit_records" in tables
        return (
            RestoreValidation(
                name="sqlite integrity",
                passed=integrity is not None and integrity[0] == "ok",
                safe_detail="ok" if integrity is not None and integrity[0] == "ok" else "failed",
            ),
            RestoreValidation(
                name="schema compatibility",
                passed=schema_ok,
                safe_detail=expected_schema if schema_ok else "incompatible",
            ),
            RestoreValidation(
                name="catalog references",
                passed=catalog_ok,
                safe_detail="ok" if catalog_ok else "invalid",
            ),
            RestoreValidation(
                name="audit structure",
                passed=audit_ok,
                safe_detail="ok" if audit_ok else "missing",
            ),
            RestoreValidation(
                name="readiness smoke",
                passed=smoke == (1,),
                safe_detail="ok" if smoke == (1,) else "failed",
            ),
        )

    def _audit_success(
        self,
        authorization: AuthorizationContext,
        correlation_id: CorrelationId,
        action: str,
        target_id: object,
    ) -> None:
        self._audit_outcome(
            authorization,
            correlation_id,
            action,
            target_id,
            AuditOutcome.SUCCEEDED,
            "recovery.operation.succeeded",
        )

    def _audit_outcome(
        self,
        authorization: AuthorizationContext,
        correlation_id: CorrelationId,
        action: str,
        target_id: object,
        outcome: AuditOutcome,
        code: str,
    ) -> None:
        self._audit.add(
            AuditRecord(
                correlation_id=correlation_id,
                actor=authorization.actor,
                action=action,
                target_type="recovery",
                target_id=str(target_id),
                outcome=outcome,
                code=code,
                policy_version="ADR-0016",
            )
        )
