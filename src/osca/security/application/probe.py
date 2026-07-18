from __future__ import annotations

from osca.security.api import SecretReference, VaultProbeResult, VaultState
from osca.security.application.ports import SecretVault


def probe_secret_reference(vault: SecretVault, reference: SecretReference) -> VaultProbeResult:
    """Probe resolvability without returning the secret through a public contract."""

    try:
        value = vault.resolve(reference)
    except PermissionError:
        return VaultProbeResult(
            reference=reference,
            state=VaultState.DENIED,
            code="VAULT_ACCESS_DENIED",
            remediation="Grant the OSCA process access to the operating-system credential store.",
        )
    except OSError:
        return VaultProbeResult(
            reference=reference,
            state=VaultState.UNAVAILABLE,
            code="VAULT_UNAVAILABLE",
            remediation="Start or unlock the configured operating-system credential store.",
        )
    if value is None:
        return VaultProbeResult(
            reference=reference,
            state=VaultState.MISSING,
            code="VAULT_REFERENCE_MISSING",
            remediation=f"Configure {reference.display_name()} through the secret setup command.",
        )
    return VaultProbeResult(
        reference=reference,
        state=VaultState.AVAILABLE,
        code="VAULT_REFERENCE_AVAILABLE",
    )

