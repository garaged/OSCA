import sqlite3

import pytest

from osca.extensions.api import (
    ExtensionCategory,
    ExtensionEntryPoint,
    ExtensionManifest,
    ExtensionPermission,
    ExtensionPermissionKind,
    ExtensionSchemaRef,
    ExtensionTrustTier,
)
from osca.extensions.application import create_installation_record, decide_activation
from osca.extensions.persistence import SQLiteExtensionLifecycleStore

DIGEST = "sha256:" + "c" * 64


def manifest(package_id: str = "stored-extension") -> ExtensionManifest:
    return ExtensionManifest(
        package_id=package_id,
        name="Stored Extension",
        publisher="garaged",
        package_version="1.0.0",
        category=ExtensionCategory.ANALYSIS,
        entry_points=(
            ExtensionEntryPoint(
                name="stored",
                contract_family="osca.analysis.graph",
                callable_ref="stored_extension:build",
            ),
        ),
        osca_compatibility=(">=0.1.0",),
        output_schemas=(
            ExtensionSchemaRef(
                name="stored_output",
                schema_family="osca.analysis.output",
                version="1.0.0",
            ),
        ),
        permissions=(
            ExtensionPermission(
                kind=ExtensionPermissionKind.PROVIDER_DATA,
                scope="market-data:read",
                rationale="Read governed bars",
            ),
        ),
        integrity_digest=DIGEST,
        license="Apache-2.0",
        provenance="local bundle fixture",
        trust_tier=ExtensionTrustTier.VERIFIED,
    )


def test_sqlite_store_round_trips_installation_records(tmp_path) -> None:
    store = SQLiteExtensionLifecycleStore(tmp_path / "extensions.sqlite")
    store.initialize()
    package = manifest()
    record = create_installation_record(
        package,
        source_uri="file:///extensions/stored-extension.oscaext",
        granted_permissions=package.permissions,
    )

    store.save_installation(record)

    restored = store.get_installation(record.installation_id)
    assert restored == record
    assert store.list_installations() == (record,)
    assert store.list_installations(package_id=package.package_id) == (record,)
    assert store.list_installations(package_id="missing") == ()


def test_sqlite_store_round_trips_activation_decisions(tmp_path) -> None:
    store = SQLiteExtensionLifecycleStore(tmp_path / "extensions.sqlite")
    store.initialize()
    package = manifest()
    record = create_installation_record(
        package,
        source_uri="file:///extensions/stored-extension.oscaext",
        granted_permissions=package.permissions,
    )
    decision = decide_activation(
        package,
        record,
        requested_permissions=package.permissions,
    )

    store.save_installation(record)
    store.save_activation_decision(decision)

    assert store.get_activation_decision(decision.decision_id) == decision
    assert store.list_activation_decisions() == (decision,)
    assert store.list_activation_decisions(installation_id=record.installation_id) == (
        decision,
    )
    assert store.list_activation_decisions_for_package(package.package_id) == (decision,)
    assert store.list_activation_decisions_for_package("missing") == ()


def test_sqlite_store_preserves_distinct_package_installations(tmp_path) -> None:
    store = SQLiteExtensionLifecycleStore(tmp_path / "extensions.sqlite")
    store.initialize()
    first = manifest(package_id="first-extension")
    second = manifest(package_id="second-extension")
    first_record = create_installation_record(
        first,
        source_uri="file:///extensions/first.oscaext",
        granted_permissions=first.permissions,
    )
    second_record = create_installation_record(
        second,
        source_uri="file:///extensions/second.oscaext",
        granted_permissions=second.permissions,
    )

    store.save_installation(second_record)
    store.save_installation(first_record)

    assert set(store.list_installations()) == {first_record, second_record}
    assert store.list_installations(package_id="first-extension") == (first_record,)
    assert store.list_installations(package_id="second-extension") == (second_record,)


def test_sqlite_store_requires_installation_before_activation_decision(tmp_path) -> None:
    store = SQLiteExtensionLifecycleStore(tmp_path / "extensions.sqlite")
    store.initialize()
    package = manifest()
    record = create_installation_record(
        package,
        source_uri="file:///extensions/stored-extension.oscaext",
        granted_permissions=package.permissions,
    )
    decision = decide_activation(
        package,
        record,
        requested_permissions=package.permissions,
    )

    with pytest.raises(sqlite3.IntegrityError):
        store.save_activation_decision(decision)
