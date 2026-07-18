from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from osca.shared_kernel.api import CorrelationId


class AuditOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    REJECTED = "rejected"
    FAILED = "failed"


class AuditRecord(BaseModel):
    """Security-relevant evidence with no arbitrary or secret-bearing payload."""

    model_config = ConfigDict(frozen=True)

    contract_family: Literal["osca.audit.record"] = "osca.audit.record"
    contract_version: Literal["1.0.0"] = "1.0.0"
    record_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: CorrelationId
    actor: str
    action: str
    target_type: str
    target_id: str
    outcome: AuditOutcome
    code: str
    policy_version: str

