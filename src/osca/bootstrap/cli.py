from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Annotated
from uuid import UUID

import typer

from osca import __version__
from osca.backtesting.api import BacktestRequest
from osca.backtesting.application import plan_backtest_execution
from osca.backtesting.persistence import SQLiteBacktestLifecycleStore
from osca.bootstrap.authorization import local_authorization_context
from osca.bootstrap.recovery import persist_configuration_snapshot, recovery_service
from osca.bootstrap.runtime import readiness_snapshot
from osca.bootstrap.workflow import workflow_service
from osca.configuration.api.contracts import RawConfiguration
from osca.configuration.application import validate_configuration
from osca.extensions.api import ExtensionManifest
from osca.extensions.application import create_installation_record, decide_activation
from osca.extensions.persistence import SQLiteExtensionLifecycleStore
from osca.provider_adapters import (
    ProviderAdapterEndpoint,
    ProviderAdapterFixture,
    build_default_preferred_no_cost_adapter_contracts,
    provider_adapter_contract_by_id,
    validate_adapter_fixture_for_contract,
)
from osca.provider_catalog import (
    ProviderCatalogIdentifier,
    build_default_no_cost_provider_profiles,
    classify_provider_implementation_readiness,
)
from osca.provider_promotion import ProviderIdentifier
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
    source_uri: Annotated[str, typer.Option("--source-uri")],
    database: Annotated[Path, typer.Option("--database")] = Path("osca-extensions.sqlite"),
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
    database: Annotated[Path, typer.Option("--database")] = Path("osca-extensions.sqlite"),
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
    database: Annotated[Path, typer.Option("--database")] = Path("osca-extensions.sqlite"),
    package_id: Annotated[str | None, typer.Option("--package-id")] = None,
) -> None:
    """List persisted extension installation records."""

    store = SQLiteExtensionLifecycleStore(database)
    store.initialize()
    records = store.list_installations(package_id=package_id)
    typer.echo(json.dumps([record.model_dump(mode="json") for record in records], indent=2))


@app.command("backtest-plan")
def backtest_plan(
    request_file: Path,
    database: Annotated[Path, typer.Option("--database")] = Path("osca-backtests.sqlite"),
) -> None:
    """Persist a backtest request and its fail-closed execution plan."""

    request = _load_backtest_request(request_file)
    store = SQLiteBacktestLifecycleStore(database)
    store.initialize()
    plan = plan_backtest_execution(request)
    store.save_request(request)
    store.save_execution_plan(plan)
    typer.echo(plan.model_dump_json(indent=2))


@app.command("backtest-list")
def backtest_list(
    database: Annotated[Path, typer.Option("--database")] = Path("osca-backtests.sqlite"),
    project_id: Annotated[UUID | None, typer.Option("--project-id")] = None,
    strategy_id: Annotated[str | None, typer.Option("--strategy-id")] = None,
) -> None:
    """List persisted backtest requests without executing strategies."""

    store = SQLiteBacktestLifecycleStore(database)
    store.initialize()
    records = store.list_requests(project_id=project_id, strategy_id=strategy_id)
    typer.echo(json.dumps([record.model_dump(mode="json") for record in records], indent=2))



@app.command("provider-catalog-list")
def provider_catalog_list(
    include_readiness: Annotated[
        bool,
        typer.Option("--include-readiness", help="Include deterministic implementation readiness."),
    ] = False,
) -> None:
    """List governed no-cost provider catalog profiles."""

    profiles = build_default_no_cost_provider_profiles()
    if include_readiness:
        payload = [
            {
                "profile": profile.model_dump(mode="json"),
                "implementation_readiness": classify_provider_implementation_readiness(
                    profile
                ).model_dump(mode="json"),
            }
            for profile in profiles
        ]
    else:
        payload = [profile.model_dump(mode="json") for profile in profiles]
    typer.echo(json.dumps(payload, indent=2))


@app.command("provider-promotion-status")
def provider_promotion_status() -> None:
    """Report production-provider promotion candidates and deferred runtime boundaries."""

    payload = {
        "providers": [
            {
                "provider_id": provider_id.value,
                "production_promotion_required": True,
                "provider_enabled": False,
                "evidence_required": [
                    "license",
                    "credential_reference",
                    "quota",
                    "retention_policy",
                    "export_policy",
                    "backup_policy",
                ],
            }
            for provider_id in ProviderIdentifier
        ],
        "deferred_boundaries": _provider_deferred_boundaries(),
    }
    typer.echo(json.dumps(payload, indent=2))


@app.command("provider-adapter-contracts")
def provider_adapter_contracts() -> None:
    """List fixture-backed preferred no-cost provider adapter contracts."""

    profiles = build_default_no_cost_provider_profiles()
    contracts = build_default_preferred_no_cost_adapter_contracts(profiles)
    payload = {
        "contracts": [contract.model_dump(mode="json") for contract in contracts],
        "deferred_boundaries": _provider_deferred_boundaries(),
    }
    typer.echo(json.dumps(payload, indent=2))


@app.command("provider-adapter-validate-fixture")
def provider_adapter_validate_fixture(
    provider_id: ProviderCatalogIdentifier,
    endpoint: ProviderAdapterEndpoint,
    fixture_name: str,
    resource_id: str,
    payload_sha256: str,
    record_count: int,
    source_uri: Annotated[str, typer.Option("--source-uri")] = "fixture://operator",
) -> None:
    """Validate fixture metadata against the governed adapter contract."""

    profiles = build_default_no_cost_provider_profiles()
    contracts = build_default_preferred_no_cost_adapter_contracts(profiles)
    contract = provider_adapter_contract_by_id(contracts, provider_id)
    if contract is None:
        raise typer.BadParameter(f"provider has no P4 adapter contract: {provider_id.value}")

    fixture = ProviderAdapterFixture(
        provider_id=provider_id,
        endpoint=endpoint,
        fixture_name=fixture_name,
        resource_id=resource_id,
        payload_sha256=payload_sha256,
        source_uri=source_uri,
        record_count=record_count,
    )
    decision = validate_adapter_fixture_for_contract(contract, fixture)
    typer.echo(decision.model_dump_json(indent=2))


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


def _provider_deferred_boundaries() -> dict[str, bool]:
    return {
        "live_provider_calls_enabled": False,
        "credential_materialization_enabled": False,
        "runtime_provider_routing_enabled": False,
        "production_ingestion_enabled": False,
        "real_capital_orders_enabled": False,
    }


def _load_backtest_request(request_file: Path) -> BacktestRequest:
    return BacktestRequest.model_validate_json(request_file.read_text(encoding="utf-8"))


def _load_extension_manifest(manifest_file: Path) -> ExtensionManifest:
    return ExtensionManifest.model_validate_json(manifest_file.read_text(encoding="utf-8"))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
