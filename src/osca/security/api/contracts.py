from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class SecretReference(BaseModel):
    model_config = ConfigDict(frozen=True)

    namespace: str = Field(min_length=1, max_length=100, pattern=r"^[a-z][a-z0-9_-]*$")
    name: str = Field(min_length=1, max_length=200, pattern=r"^[A-Za-z0-9._/-]+$")

    def display_name(self) -> str:
        return f"vault://{self.namespace}/{self.name}"


class VaultState(StrEnum):
    AVAILABLE = "available"
    MISSING = "missing"
    DENIED = "denied"
    UNAVAILABLE = "unavailable"


class VaultProbeResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    reference: SecretReference
    state: VaultState
    code: str
    remediation: str | None = None


class Capability(StrEnum):
    WORKFLOW_SUBMIT = "workflow.diagnostic.submit"
    WORKFLOW_READ = "workflow.diagnostic.read"
    WORKFLOW_CANCEL = "workflow.diagnostic.cancel"


class AuthorizationContext(BaseModel):
    """Identity and capabilities established by a trusted adapter boundary."""

    model_config = ConfigDict(frozen=True)
    actor: str = Field(min_length=1, max_length=200)
    capabilities: frozenset[Capability]
    authentication_method: str
