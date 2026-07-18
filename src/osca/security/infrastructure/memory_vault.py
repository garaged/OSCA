from __future__ import annotations

from osca.security.api import SecretReference


class InMemoryVault:
    """Non-production deterministic adapter for tests and conformance fixtures."""

    def __init__(self) -> None:
        self._values: dict[tuple[str, str], str] = {}

    @staticmethod
    def _key(reference: SecretReference) -> tuple[str, str]:
        return reference.namespace, reference.name

    def store(self, reference: SecretReference, value: str) -> None:
        if not value:
            raise ValueError("secret value cannot be empty")
        self._values[self._key(reference)] = value

    def resolve(self, reference: SecretReference) -> str | None:
        return self._values.get(self._key(reference))

    def delete(self, reference: SecretReference) -> bool:
        return self._values.pop(self._key(reference), None) is not None

