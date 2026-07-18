from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from osca.shared_kernel.api import CorrelationId


class HealthState(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    BLOCKED = "blocked"
    RECOVERING = "recovering"
    UNAVAILABLE = "unavailable"


class ComponentReadiness(BaseModel):
    model_config = ConfigDict(frozen=True)

    component: str
    required: bool
    state: HealthState
    code: str
    impact: str | None = None
    remediation: str | None = None


class ReadinessSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    contract_family: Literal["osca.readiness.snapshot"] = "osca.readiness.snapshot"
    contract_version: Literal["1.0.0"] = "1.0.0"
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: CorrelationId
    configuration_revision: UUID
    product_version: str
    state: HealthState
    components: tuple[ComponentReadiness, ...]

