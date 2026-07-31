from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class OnboardingStatus(StrEnum):
    READY = "ready"
    ACTION_REQUIRED = "action_required"
    FAILED = "failed"


class OnboardingCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    check_id: str
    status: OnboardingStatus
    summary: str
    remediation: str | None = None


class OnboardingReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: OnboardingStatus
    storage_root: str
    prepared: bool
    checks: tuple[OnboardingCheck, ...]
    next_commands: tuple[str, ...]
    network_used: bool = False
    credentials_used: bool = False
    recommendations_enabled: bool = False
    broker_execution_enabled: bool = False
    real_capital_enabled: bool = False
