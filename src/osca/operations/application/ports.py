from __future__ import annotations

from typing import Protocol
from uuid import UUID

from osca.operations.api import AuditRecord


class AuditRepository(Protocol):
    def add(self, record: AuditRecord) -> None: ...

    def get(self, record_id: UUID) -> AuditRecord | None: ...

