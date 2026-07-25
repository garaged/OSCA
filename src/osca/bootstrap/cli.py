from __future__ import annotations

import hashlib
import json
from pathlib import Path
from uuid import UUID

import typer

from osca import __version__
from osca.bootstrap.authorization import local_authorization_context
from osca.bootstrap.recovery import persist_configuration_snapshot, recovery_service
from osca.bootstrap.runtime import readiness_snapshot
from osca.bootstrap.workflow import workflow_service
from osca.configuration.api.contracts import RawConfiguration
from osca.configuration.application import validate_configuration
from osca.extensions.api import ExtensionManifest
from osca.extensions.application import create_installation_record, decide_activation
from osca.extensions.persistence import SQLiteExtensionLifecycleStore
from osca.recovery.api import CreateBackup, ExecuteRestore, PreviewRestore, VerifyBackup
from osca.security.api import SecretReference
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import (
    CancelDiagnosticRun,
    DiagnosticInput,
    DiagnosticRunId,
    GetDiagnosticRun,
    ListDiagnosticRuns,
    SubmitDiagnosticRun,
)

app = typer.Typer(no_args_is_help=True, help="OSCA operator command line.")


@app.callback()
def cli() -> None:
    """Operate and inspect a local or personal-server OSCA installation."""


@app.command()
def readiness() -> None:
    """Report the validated local readiness snapshot."""

    typer.echo(json.dumps(readiness_snapshot().model_dump(mode="json"), indent=2))


@app.command("diagnostic-submit")
def diagnostic_submit(probe: str, idempotency_key: str) -> None:
    """Submit a durable versioned diagnostic run."""
    command = SubmitDiagnosticRun(
        authorization=local_authorization_context(),
        correlation_id=CorrelationId.new(),
        idempotency_key=idempotency_key,
        input=DiagnosticInput(probe=probe),
    )
    with workflow_service() as service:
        run = service.submit(command)
    typer.echo(run.model_dump_json(indent=2))


@app.command("diagnostic-get")
def diagnostic_get(run_id: UUID) -> None:
    """Get a durable diagnostic run."""
    with workflow_service() as service:
        run = service.get(
            GetDiagnosticRun(
                authorization=local_authorization_context(), run_id=DiagnosticRunId(value=run_id)
            )
        )
    typer.echo(run.model_dump_json(indent=2))


@app.command("diagnostic-list")
def diagnostic_list(limit: int = 100) -> None:
    """List durable diagnostic runs."""
    with workflow_service() as service:
        runs = service.list(
            ListDiagnosticRuns(authorization=local_authorization_context(), limit=limit)
        )
    typer.echo(json.dumps([run.model_dump(mode="json") for run in runs], indent=2))


@app.command("diagnostic-cancel")
def diagnostic_cancel(run_id: UUID) -> None:
    """Request cancellation of a durable diagnostic run."""
    command = CancelDiagnosticRun(
        authorization=local_authorization_context(),
        correlation_id=CorrelationId.new(),
        run_id=DiagnosticRunId(value=run_id),
    )
    with workflow_service() as service:
        run = service.cancel(command)
    typer.echo(run.model_dump_json(indent=2))


@app.command("extension-install")
def extension_install(
    manifest_file: Path,
    source_uri: str = typer.Option(..., "--source-uri"),
    database: Path = typer.Option(Path("osca-extensions.sqlite"), "--database"),
) -> None:
    """Create and persist an extension installation record from a manifest."""

    manifest = _load_extension_manifest(manifest_file)
    store = SQLiteExtensionLifecycleStore(database)
    store.initialize()
    record = create_installation_record(
        manifest,
        source_uri=source_uri,
        granted_permissions=manifest.permissions,
    )
    store.save_installation(record)
    typer.echo(record.model_dump_json(indent=2))


@app.command("extension-activate")
def extension_activate(
    manifest_file: Path,
    installation_id: UUID,
    database: Path = typer.Option(Path("osca-extensions.sqlite"), "--database"),
) -> None:
    """Record an explicit extension activation decision."""

    manifest = _load_extension_manifest(manifest_file)
    store = SQLiteExtensionLifecycleStore(database)
    store.initialize()
    installation = store.get_installation(installation_id)
    if installation is None:
        raise typer.BadParameter(f"installation not found: {installation_id}")
    decision = decide_activation(
        manifest,
        installation,
        requested_permissions=manifest.permissions,
    )
    store.save_activation_decision(decision)
    typer.echo(decision.model_dump_json(indent=2))


@app.command("extension-list")
def extension_list(
    database: Path = typer.Option(Path("osca-extensions.sqlite"), "--database"),
    package_id: str | None = typer.Option(None, "--package-id"),
) -> None:
    """List persisted extension installation records."""

    store = SQLiteExtensionLifecycleStore(database)
    store.initialize()
    records = store.list_installations(package_id=package_id)
    typer.echo(json.dumps([record.model_dump(mode="json") for record in records], indent=2))


@app.command("backup-create")
def backup_create(destination: Path, recipient: str) -> None:
    """Create an encrypted age v1 backup of governed M1 state."""
    configuration = validate_configuration(RawConfiguration())
    persist_configuration_snapshot(configuration)
    fingerprint = "sha256:" + hashlib.sha256(recipient.encode()).hexdigest()
    command = CreateBackup(
        authorization=local_authorization_context(),
        correlation_id=CorrelationId.new(),
        destination=str(destination),
        recipient=recipient,
        recipient_fingerprint=fingerprint,
        configuration_snapshot=configuration,
        configuration_revision=configuration.revision_id,
        source_build=__version__,
        source_schema="m1_0006",
    )
    with recovery_service() as service:
        record = service.create(command)
    typer.echo(record.model_dump_json(indent=2))


@app.command("backup-verify")
def backup_verify(package: Path, identity_name: str) -> None:
    """Authenticate and verify a protected backup without active-state writes."""
    query = VerifyBackup(
        authorization=local_authorization_context(),
        correlation_id=CorrelationId.new(),
        package=str(package),
        identity_reference=SecretReference(namespace="recovery", name=identity_name),
    )
    with recovery_service() as service:
        manifest, digest = service.verify(query)
    typer.echo(
        json.dumps(
            {"package_digest": digest, "manifest": manifest.model_dump(mode="json")},
            indent=2,
        )
    )


@app.command("restore-preview")
def restore_preview(package: Path, destination: Path, identity_name: str) -> None:
    """Preview an isolated restore and report conflicts."""
    query = PreviewRestore(
        authorization=local_authorization_context(),
        correlation_id=CorrelationId.new(),
        package=str(package),
        destination=str(destination),
        identity_reference=SecretReference(namespace="recovery", name=identity_name),
    )
    with recovery_service() as service:
        plan = service.preview(query)
    typer.echo(plan.model_dump_json(indent=2))


@app.command("restore-isolated")
def restore_isolated(package: Path, destination: Path, identity_name: str) -> None:
    """Verify, preview, and restore into a new isolated destination."""
    correlation = CorrelationId.new()
    identity = SecretReference(namespace="recovery", name=identity_name)
    authorization = local_authorization_context()
    with recovery_service() as service:
        plan = service.preview(
            PreviewRestore(
                authorization=authorization,
                correlation_id=correlation,
                package=str(package),
                destination=str(destination),
                identity_reference=identity,
            )
        )
        record = service.execute(
            ExecuteRestore(
                authorization=authorization,
                correlation_id=correlation,
                package=str(package),
                identity_reference=identity,
                plan=plan,
            )
        )
    typer.echo(record.model_dump_json(indent=2))


def _load_extension_manifest(manifest_file: Path) -> ExtensionManifest:
    return ExtensionManifest.model_validate_json(manifest_file.read_text(encoding="utf-8"))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
