from __future__ import annotations

from typing import Protocol

from osca.security.api import SecretReference


class SecretVault(Protocol):
    def store(self, reference: SecretReference, value: str) -> None: ...

    def resolve(self, reference: SecretReference) -> str | None: ...

    def delete(self, reference: SecretReference) -> bool: ...

