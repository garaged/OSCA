"""D3 provider-policy and credential-vault application helpers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from osca.production_ingestion.contracts import (
    AdmissionStatus,
    ProductionProvider,
    ProviderAdmissionDecision,
)
from osca.production_ingestion.policy import admission_for, provider_admission_policy
from osca.security.api import SecretReference, VaultProbeResult, VaultState
from osca.security.application.ports import SecretVault
from osca.security.application.probe import probe_secret_reference

_NAMED_SECRET_MODE = "named-secret-reference"
_D3_ACQUISITION_RESOURCES: dict[ProductionProvider, frozenset[str]] = {
    ProductionProvider.KRAKEN: frozenset({"spot_ohlc"}),
}


class DataSourceError(ValueError):
    """Display-safe D3 data-source failure with a stable code."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


def provider_catalog(vault: SecretVault) -> dict[str, Any]:
    """Return policy-derived provider capability rows without secret values."""

    return {
        "family": "osca.desktop-provider-catalog.result",
        "version": "1.0.0",
        "providers": [
            _provider_row(vault, decision) for decision in provider_admission_policy()
        ],
        "offline_paths": [
            {
                "id": "bundled-synthetic-sample",
                "label": "Bundled synthetic sample",
                "network_required": False,
                "credential_required": False,
                "available": True,
            },
            {
                "id": "governed-local-csv-import",
                "label": "Governed local CSV import",
                "network_required": False,
                "credential_required": False,
                "available": True,
            },
        ],
        "network_access_enabled": False,
        "network_consent_mode": "explicit-per-acquisition-request",
        "provider_promotion_automatic": False,
        "recommendations_enabled": False,
        "live_execution_enabled": False,
    }


def store_provider_credential(
    vault: SecretVault,
    provider_id: ProductionProvider,
    value: str,
) -> dict[str, Any]:
    """Store a provider secret and return only display-safe metadata."""

    reference = credential_reference_for(provider_id)
    if not value:
        raise DataSourceError("invalid_parameters", "credential value cannot be empty")
    if len(value) > 8192:
        raise DataSourceError("invalid_parameters", "credential value exceeds 8192 characters")
    try:
        vault.store(reference, value)
    except PermissionError as exc:
        raise DataSourceError(
            "vault_access_denied",
            "The operating-system credential store denied access.",
        ) from exc
    except Exception as exc:
        raise DataSourceError(
            "vault_unavailable",
            "The operating-system credential store is unavailable.",
            retryable=True,
        ) from exc
    return _credential_result(
        provider_id,
        operation="stored",
        probe=_safe_probe(vault, reference),
    )


def probe_provider_credential(
    vault: SecretVault,
    provider_id: ProductionProvider,
) -> dict[str, Any]:
    """Probe a provider secret without returning its value."""

    reference = credential_reference_for(provider_id)
    return _credential_result(
        provider_id,
        operation="probed",
        probe=_safe_probe(vault, reference),
    )


def delete_provider_credential(
    vault: SecretVault,
    provider_id: ProductionProvider,
) -> dict[str, Any]:
    """Delete a provider secret and return only its final presence state."""

    reference = credential_reference_for(provider_id)
    try:
        deleted = vault.delete(reference)
    except PermissionError as exc:
        raise DataSourceError(
            "vault_access_denied",
            "The operating-system credential store denied access.",
        ) from exc
    except Exception as exc:
        raise DataSourceError(
            "vault_unavailable",
            "The operating-system credential store is unavailable.",
            retryable=True,
        ) from exc
    return {
        **_credential_result(
            provider_id,
            operation="deleted" if deleted else "already-missing",
            probe=_safe_probe(vault, reference),
        ),
        "deleted": deleted,
    }


def credential_reference_for(provider_id: ProductionProvider) -> SecretReference:
    """Return the stable named secret reference accepted by provider policy."""

    decision = admission_for(provider_id)
    if decision.credential_mode != _NAMED_SECRET_MODE:
        raise DataSourceError(
            "credential_not_required",
            f"{provider_id.value} does not use a named credential in the accepted policy",
        )
    return SecretReference(namespace="provider", name=f"{provider_id.value}/api-key")


def parse_provider_id(value: object) -> ProductionProvider:
    if not isinstance(value, str) or not value.strip():
        raise DataSourceError("invalid_parameters", "provider_id must be a non-empty string")
    try:
        return ProductionProvider(value)
    except ValueError as exc:
        raise DataSourceError("provider_not_found", "Unknown provider identifier.") from exc


def _provider_row(
    vault: SecretVault,
    decision: ProviderAdmissionDecision,
) -> dict[str, Any]:
    credential_state = "not_required"
    credential_code = "CREDENTIAL_NOT_REQUIRED"
    credential_remediation: str | None = None
    credential_reference: str | None = None
    credential_actions: tuple[str, ...] = ()
    if decision.credential_mode == _NAMED_SECRET_MODE:
        reference = credential_reference_for(decision.provider_id)
        probe = _safe_probe(vault, reference)
        credential_state = probe.state.value
        credential_code = probe.code
        credential_remediation = probe.remediation
        credential_reference = reference.display_name()
        credential_actions = (
            "credential.store",
            "credential.probe",
            "credential.delete",
        )

    supported_resources = _D3_ACQUISITION_RESOURCES.get(
        decision.provider_id,
        frozenset(),
    )
    runnable_resources = tuple(
        resource
        for resource in decision.approved_resources
        if resource in supported_resources
    )
    acquisition_available = (
        decision.status is AdmissionStatus.APPROVED and bool(runnable_resources)
    )
    acquisition_actions = ("acquisition.submit",) if acquisition_available else ()
    actions = (*credential_actions, *acquisition_actions)
    return {
        "provider_id": decision.provider_id.value,
        "admission_status": decision.status.value,
        "approved_resources": list(decision.approved_resources),
        "d3_acquisition_resources": list(runnable_resources),
        "internal_use_only": decision.internal_use_only,
        "redistribution_enabled": False,
        "credential_mode": decision.credential_mode,
        "credential_reference": credential_reference,
        "credential_state": credential_state,
        "credential_code": credential_code,
        "credential_remediation": credential_remediation,
        "network_required": acquisition_available,
        "acquisition_available": acquisition_available,
        "available_actions": list(actions),
        "terms_reference_uri": decision.terms_reference_uri,
        "evidence_reviewed_at": decision.evidence_reviewed_at.isoformat(),
        "rationale": decision.rationale,
        "findings": list(decision.findings),
        "promotion_automatic": False,
    }


def _credential_result(
    provider_id: ProductionProvider,
    *,
    operation: str,
    probe: VaultProbeResult,
) -> dict[str, Any]:
    decision = admission_for(provider_id)
    supported = _D3_ACQUISITION_RESOURCES.get(provider_id, frozenset())
    runnable = tuple(resource for resource in decision.approved_resources if resource in supported)
    return {
        "family": "osca.desktop-provider-credential.result",
        "version": "1.0.0",
        "operation": operation,
        "provider_id": provider_id.value,
        "reference": probe.reference.display_name(),
        "state": probe.state.value,
        "code": probe.code,
        "remediation": probe.remediation,
        "admission_status": decision.status.value,
        "approved_resources": list(decision.approved_resources),
        "acquisition_available": (
            decision.status is AdmissionStatus.APPROVED and bool(runnable)
        ),
        "provider_promotion_automatic": False,
        "secret_value_returned": False,
    }


def _safe_probe(vault: SecretVault, reference: SecretReference) -> VaultProbeResult:
    try:
        return probe_secret_reference(vault, reference)
    except Exception:
        return VaultProbeResult(
            reference=reference,
            state=VaultState.UNAVAILABLE,
            code="VAULT_UNAVAILABLE",
            remediation="Start or unlock the operating-system credential store and retry.",
        )


def provider_ids(rows: Iterable[ProviderAdmissionDecision] | None = None) -> tuple[str, ...]:
    """Return stable policy provider identifiers for validation and tests."""

    return tuple(
        decision.provider_id.value
        for decision in (rows if rows is not None else provider_admission_policy())
    )
