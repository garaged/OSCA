"""Schema-validated protocol contracts for desktop host communication."""

from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field

PROTOCOL_VERSION: Final[Literal["1.0"]] = "1.0"


class DesktopRequest(BaseModel):
    """One request sent by the trusted desktop broker to the Python sidecar."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    protocol_version: Literal["1.0"] = PROTOCOL_VERSION
    request_id: str = Field(min_length=1, max_length=128)
    method: str = Field(min_length=1, max_length=128)
    params: dict[str, Any] = Field(default_factory=dict)


class DesktopError(BaseModel):
    """Stable machine-readable error returned across the desktop boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    message: str
    retryable: bool = False


class DesktopResponse(BaseModel):
    """One response emitted by the Python sidecar."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    protocol_version: Literal["1.0"] = PROTOCOL_VERSION
    request_id: str
    status: Literal["ok", "error"]
    result: dict[str, Any] | None = None
    error: DesktopError | None = None
