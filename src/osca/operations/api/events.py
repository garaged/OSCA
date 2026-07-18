from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from osca.shared_kernel.api import CorrelationId


class WorkflowJobEvent(BaseModel):
    """Safe Operations-owned evidence for a Workflow lifecycle fact."""

    model_config = ConfigDict(frozen=True)
    contract_family: Literal["osca.workflow.job-event"] = "osca.workflow.job-event"
    contract_version: Literal["1.0.0"] = "1.0.0"
    event_id: UUID = Field(default_factory=uuid4)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    correlation_id: CorrelationId
    run_id: UUID
    action: str
    state: str
    attempt: int
    outcome: str
