"""Public Workflow contracts governed by REQ-0011--REQ-0015 and ADR-0013."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from osca.shared_kernel.api import CorrelationId

CONTRACT_FAMILY: Literal["osca.workflow.diagnostic-run"] = "osca.workflow.diagnostic-run"
CONTRACT_VERSION: Literal["1.0.0"] = "1.0.0"
GOVERNING_REQUIREMENTS = ("REQ-0011", "REQ-0012", "REQ-0013", "REQ-0014", "REQ-0015")
GOVERNING_DECISION = "ADR-0013"


class DiagnosticRunState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    BLOCKED = "blocked"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


class DiagnosticRunId(BaseModel):
    model_config = ConfigDict(frozen=True)
    value: UUID = Field(default_factory=uuid4)


class DiagnosticInput(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.workflow.diagnostic-input"] = "osca.workflow.diagnostic-input"
    version: Literal["1.0.0"] = "1.0.0"
    probe: str = Field(min_length=1, max_length=100)
    parameters: dict[str, str] = Field(default_factory=dict)


class DiagnosticCheckpoint(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.workflow.diagnostic-checkpoint"] = "osca.workflow.diagnostic-checkpoint"
    version: Literal["1.0.0"] = "1.0.0"
    phase: int = Field(ge=0, le=3)
    completed_phases: tuple[str, ...] = ()


class DiagnosticResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.catalog.result-reference"] = "osca.catalog.result-reference"
    version: Literal["1.0.0"] = "1.0.0"
    result_id: UUID
    media_type: str = "application/json"


class DiagnosticRunError(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.error.envelope"] = "osca.error.envelope"
    version: Literal["1.0.0"] = "1.0.0"
    code: str
    message: str
    retryable: bool = False


class DiagnosticRun(BaseModel):
    model_config = ConfigDict(frozen=True)
    contract_family: Literal["osca.workflow.diagnostic-run"] = CONTRACT_FAMILY
    contract_version: Literal["1.0.0"] = CONTRACT_VERSION
    run_id: DiagnosticRunId = Field(default_factory=DiagnosticRunId)
    correlation_id: CorrelationId
    actor: str
    idempotency_key: str
    input: DiagnosticInput
    state: DiagnosticRunState = DiagnosticRunState.PENDING
    revision: int = 0
    attempt: int = 0
    checkpoint: DiagnosticCheckpoint | None = None
    result: DiagnosticResult | None = None
    error: DiagnosticRunError | None = None
    lease_owner: str | None = None
    lease_expires_at: datetime | None = None
    next_attempt_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SubmitDiagnosticRun(BaseModel):
    model_config = ConfigDict(frozen=True)
    actor: str
    correlation_id: CorrelationId
    idempotency_key: str = Field(min_length=1, max_length=200)
    input: DiagnosticInput


class CancelDiagnosticRun(BaseModel):
    model_config = ConfigDict(frozen=True)
    actor: str
    correlation_id: CorrelationId
    run_id: DiagnosticRunId


class GetDiagnosticRun(BaseModel):
    model_config = ConfigDict(frozen=True)
    run_id: DiagnosticRunId


class ListDiagnosticRuns(BaseModel):
    model_config = ConfigDict(frozen=True)
    states: tuple[DiagnosticRunState, ...] = ()
    limit: int = Field(default=100, ge=1, le=500)
