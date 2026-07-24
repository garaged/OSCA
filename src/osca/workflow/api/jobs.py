from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from osca.catalog.api import metadata_digest
from osca.security.api import AuthorizationContext
from osca.shared_kernel.api import CorrelationId


class JobState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    BLOCKED = "blocked"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


class JobResultReference(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: str = Field(min_length=1, max_length=128)
    reference_id: UUID
    revision_id: UUID | None = None


class JobError(BaseModel):
    model_config = ConfigDict(frozen=True)
    code: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=256)
    retryable: bool = False


class JobRun(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.workflow.job-run"] = "osca.workflow.job-run"
    version: Literal["1.0.0"] = "1.0.0"
    job_id: UUID = Field(default_factory=uuid4)
    correlation_id: CorrelationId
    actor: str = Field(min_length=1, max_length=200)
    kind: str = Field(min_length=1, max_length=128, pattern=r"^[a-z][a-z0-9.-]+$")
    idempotency_key: str = Field(min_length=1, max_length=200)
    input_family: str = Field(min_length=1, max_length=128)
    input_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    input_payload: dict[str, Any]
    input_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    state: JobState = JobState.PENDING
    revision: int = Field(default=0, ge=0)
    attempt: int = Field(default=0, ge=0)
    checkpoint: dict[str, Any] | None = None
    result: JobResultReference | None = None
    error: JobError | None = None
    lease_owner: str | None = None
    lease_expires_at: datetime | None = None
    next_attempt_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_terminal_result(self) -> Self:
        if self.state is JobState.SUCCEEDED and self.result is None:
            raise ValueError("succeeded job requires a durable result reference")
        return self

    def verify_input(self) -> bool:
        return self.input_digest == metadata_digest(self.input_payload)


class SubmitJob(BaseModel):
    model_config = ConfigDict(frozen=True)
    authorization: AuthorizationContext
    correlation_id: CorrelationId
    kind: str = Field(min_length=1, max_length=128, pattern=r"^[a-z][a-z0-9.-]+$")
    idempotency_key: str = Field(min_length=1, max_length=200)
    input_family: str = Field(min_length=1, max_length=128)
    input_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    input_payload: dict[str, Any]


class GetJob(BaseModel):
    model_config = ConfigDict(frozen=True)
    authorization: AuthorizationContext
    job_id: UUID


class CancelJob(GetJob):
    pass
