from __future__ import annotations

from typing import Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class CorrelationId(BaseModel):
    """Immutable correlation identity shared across public boundaries."""

    model_config = ConfigDict(frozen=True)

    value: UUID = Field(default_factory=uuid4)

    @classmethod
    def new(cls) -> Self:
        return cls()

