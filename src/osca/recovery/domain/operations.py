from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from osca.shared_kernel.api import CorrelationId


class RecoveryAction(StrEnum):
    CREATE = "backup.create"
    VERIFY = "backup.verify"
    PREVIEW = "restore.preview"
    EXECUTE = "restore.execute"


class RecoveryState(StrEnum):
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class RecoveryOperation(BaseModel):
    model_config = ConfigDict(frozen=True)
    operation_id: UUID = Field(default_factory=uuid4)
    correlation_id: CorrelationId
    actor: str
    action: RecoveryAction
    state: RecoveryState = RecoveryState.RUNNING
    target: str
    code: str = "recovery.operation.started"
    revision: int = 1
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
