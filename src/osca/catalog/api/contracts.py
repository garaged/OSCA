from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from osca.shared_kernel.api import CorrelationId


class CatalogResultReference(BaseModel):
    model_config = ConfigDict(frozen=True)
    family: Literal["osca.catalog.result-reference"] = "osca.catalog.result-reference"
    version: Literal["1.0.0"] = "1.0.0"
    result_id: UUID = Field(default_factory=uuid4)
    producing_run_id: UUID
    correlation_id: CorrelationId
    media_type: str = "application/json"
    registered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
