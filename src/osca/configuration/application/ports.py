from __future__ import annotations

from typing import Protocol
from uuid import UUID

from osca.configuration.api import ValidatedConfiguration


class ConfigurationRepository(Protocol):
    def add(self, configuration: ValidatedConfiguration) -> None: ...

    def get(self, revision_id: UUID) -> ValidatedConfiguration | None: ...

