from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128)]
Description = Annotated[str, Field(min_length=1, max_length=2048)]


class OperationsStatus(StrEnum):
    SUCCEEDED = "succeeded"
    SKIPPED = "skipped"
    POLICY_BLOCKED = "policy_blocked"
    FAILED = "failed"


class AlertTransport(StrEnum):
    FILE = "file"
    WEBHOOK = "webhook"


class PersonalServerSecurity(BaseModel):
    model_config = ConfigDict(frozen=True)

    bind_host: str = "127.0.0.1"
    tls_enabled: bool = False
    authentication_enabled: bool = False
    session_cookie_secure: bool = True
    trusted_proxy_count: int = Field(default=0, ge=0, le=8)

    @model_validator(mode="after")
    def validate_security(self) -> Self:
        loopback = self.bind_host in {"127.0.0.1", "::1", "localhost"}
        if not loopback and not (self.tls_enabled and self.authentication_enabled):
            raise ValueError(
                "non-loopback personal-server binding requires TLS and authentication"
            )
        if self.tls_enabled and not self.session_cookie_secure:
            raise ValueError("TLS deployments require secure session cookies")
        return self


class ScheduledJob(BaseModel):
    model_config = ConfigDict(frozen=True)

    job_id: Identifier
    command: tuple[Identifier, ...] = Field(min_length=1)
    interval_seconds: int = Field(ge=60, le=604800)
    enabled: bool = False
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    working_directory: str = "."


class JobRunEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.personal-server.job-run"] = "osca.personal-server.job-run"
    version: Literal["1.0.0"] = "1.0.0"
    run_id: UUID = Field(default_factory=uuid4)
    job_id: Identifier
    status: OperationsStatus
    exit_code: int | None = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    stdout_uri: str | None = None
    stderr_uri: str | None = None
    rationale: Description
    findings: tuple[Identifier, ...] = ()


class AlertRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    alert_id: UUID = Field(default_factory=uuid4)
    transport: AlertTransport
    subject: Identifier
    message: Description
    destination: str
    enabled: bool = False
    timeout_seconds: int = Field(default=10, ge=1, le=30)

    @model_validator(mode="after")
    def validate_destination(self) -> Self:
        if self.transport is AlertTransport.WEBHOOK:
            if not self.destination.startswith("https://"):
                raise ValueError("webhook alerts require HTTPS destinations")
        elif self.destination.startswith(("http://", "https://")):
            raise ValueError("file alerts require a filesystem destination")
        return self


class AlertEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.personal-server.alert"] = "osca.personal-server.alert"
    version: Literal["1.0.0"] = "1.0.0"
    alert_id: UUID
    status: OperationsStatus
    transport: AlertTransport
    destination_redacted: str
    delivered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    rationale: Description
    findings: tuple[Identifier, ...] = ()


class BackupRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_root: str
    destination_root: str
    enabled: bool = False
    include_paths: tuple[Identifier, ...] = ("state", "production-ingestion")


class BackupEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.personal-server.backup"] = "osca.personal-server.backup"
    version: Literal["1.0.0"] = "1.0.0"
    backup_id: UUID = Field(default_factory=uuid4)
    status: OperationsStatus
    archive_uri: str | None = None
    manifest_uri: str | None = None
    sha256: str | None = None
    file_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    rationale: Description
    findings: tuple[Identifier, ...] = ()


class RestoreRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    archive_path: str
    destination_root: str
    enabled: bool = False
    overwrite: bool = False


class RestoreEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    family: Literal["osca.personal-server.restore"] = "osca.personal-server.restore"
    version: Literal["1.0.0"] = "1.0.0"
    restore_id: UUID = Field(default_factory=uuid4)
    status: OperationsStatus
    restored_file_count: int = 0
    destination_uri: str | None = None
    verified_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    rationale: Description
    findings: tuple[Identifier, ...] = ()
