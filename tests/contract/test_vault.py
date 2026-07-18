from collections.abc import Callable
from typing import Protocol

import pytest

from osca.security.api import SecretReference, VaultState
from osca.security.application import SecretVault, probe_secret_reference
from osca.security.infrastructure import InMemoryVault, KeyringVault


class FakeKeyring:
    def __init__(self) -> None:
        self.values: dict[tuple[str, str], str] = {}

    def set_password(self, service_name: str, username: str, password: str) -> None:
        self.values[(service_name, username)] = password

    def get_password(self, service_name: str, username: str) -> str | None:
        return self.values.get((service_name, username))

    def delete_password(self, service_name: str, username: str) -> None:
        del self.values[(service_name, username)]


class VaultFactory(Protocol):
    def __call__(self) -> SecretVault: ...


@pytest.mark.parametrize(
    "factory",
    [InMemoryVault, lambda: KeyringVault(FakeKeyring())],
)
def test_vault_adapter_conformance(factory: Callable[[], SecretVault]) -> None:
    vault = factory()
    reference = SecretReference(namespace="provider", name="example/key")

    assert vault.resolve(reference) is None
    assert probe_secret_reference(vault, reference).state is VaultState.MISSING

    vault.store(reference, "canary-secret-value")
    assert vault.resolve(reference) == "canary-secret-value"
    assert probe_secret_reference(vault, reference).state is VaultState.AVAILABLE

    vault.store(reference, "rotated-value")
    assert vault.resolve(reference) == "rotated-value"
    assert vault.delete(reference)
    assert not vault.delete(reference)


def test_public_probe_never_contains_secret_value() -> None:
    vault = InMemoryVault()
    reference = SecretReference(namespace="provider", name="example")
    vault.store(reference, "canary-secret-value")
    serialized = probe_secret_reference(vault, reference).model_dump_json()
    assert "canary-secret-value" not in serialized

