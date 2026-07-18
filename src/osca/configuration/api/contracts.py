from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from ipaddress import IPv4Address, IPv6Address
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

IPAddress = IPv4Address | IPv6Address
Port = Annotated[int, Field(ge=1, le=65535)]


class DeploymentMode(StrEnum):
    LOCAL = "local"
    PERSONAL_SERVER = "personal_server"


class ListenerConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    host: IPAddress = IPv4Address("127.0.0.1")
    port: Port = 8080


class SecurityConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    tls_certificate_reference: str | None = None
    tls_private_key_reference: str | None = None
    trust_store_reference: str | None = None
    session_provider: str | None = None


class RawConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    profile: str = "local"
    deployment_mode: DeploymentMode = DeploymentMode.LOCAL
    listener: ListenerConfiguration = Field(default_factory=ListenerConfiguration)
    security: SecurityConfiguration = Field(default_factory=SecurityConfiguration)


class ConfigurationError(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    field: str
    message: str
    remediation: str


class ValidatedConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    contract_family: Literal["osca.configuration.snapshot"] = "osca.configuration.snapshot"
    contract_version: Literal["1.0.0"] = "1.0.0"
    revision_id: UUID = Field(default_factory=uuid4)
    validated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    profile: str
    deployment_mode: DeploymentMode
    listener: ListenerConfiguration
    security: SecurityConfiguration

