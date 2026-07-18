from __future__ import annotations

from typing import Protocol

import keyring

from osca.security.api import SecretReference


class KeyringBackend(Protocol):
    def set_password(self, service_name: str, username: str, password: str) -> None: ...

    def get_password(self, service_name: str, username: str) -> str | None: ...

    def delete_password(self, service_name: str, username: str) -> None: ...


class KeyringVault:
    def __init__(self, backend: KeyringBackend = keyring) -> None:
        self._backend = backend

    @staticmethod
    def _service(reference: SecretReference) -> str:
        return f"osca.{reference.namespace}"

    def store(self, reference: SecretReference, value: str) -> None:
        if not value:
            raise ValueError("secret value cannot be empty")
        self._backend.set_password(self._service(reference), reference.name, value)

    def resolve(self, reference: SecretReference) -> str | None:
        return self._backend.get_password(self._service(reference), reference.name)

    def delete(self, reference: SecretReference) -> bool:
        if self.resolve(reference) is None:
            return False
        self._backend.delete_password(self._service(reference), reference.name)
        return True

