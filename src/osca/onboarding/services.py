from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

from osca.onboarding.contracts import OnboardingCheck, OnboardingReport, OnboardingStatus

_SUPPORTED_PYTHON = (3, 13)


def inspect_first_run(storage_root: Path, *, prepare: bool = False) -> OnboardingReport:
    checks: list[OnboardingCheck] = []

    python_ready = sys.version_info[:2] == _SUPPORTED_PYTHON
    checks.append(
        OnboardingCheck(
            check_id="python-version",
            status=OnboardingStatus.READY if python_ready else OnboardingStatus.ACTION_REQUIRED,
            summary=(
                f"Python {sys.version_info.major}.{sys.version_info.minor} is supported."
                if python_ready
                else "OSCA requires Python 3.13."
            ),
            remediation=None if python_ready else "Install Python 3.13 and run uv sync --locked.",
        )
    )

    platform_ready = sys.platform.startswith("linux") or sys.platform == "darwin"
    checks.append(
        OnboardingCheck(
            check_id="platform",
            status=OnboardingStatus.READY if platform_ready else OnboardingStatus.ACTION_REQUIRED,
            summary=f"Detected {platform.system()} {platform.machine()}.",
            remediation=(
                None
                if platform_ready
                else "Use the supported Linux x86_64 or macOS arm64 environment."
            ),
        )
    )

    storage_check = _inspect_storage(storage_root, prepare=prepare)
    checks.append(storage_check)

    fixture = Path("tests/fixtures/local_ohlcv/aapl_backtest_daily.csv")
    fixture_ready = fixture.is_file()
    checks.append(
        OnboardingCheck(
            check_id="demo-fixture",
            status=OnboardingStatus.READY if fixture_ready else OnboardingStatus.ACTION_REQUIRED,
            summary=(
                "The committed AAPL onboarding fixture is available."
                if fixture_ready
                else "The committed AAPL onboarding fixture was not found."
            ),
            remediation=(
                None
                if fixture_ready
                else "Run onboarding from the OSCA repository root or restore the test fixtures."
            ),
        )
    )

    checks.append(
        OnboardingCheck(
            check_id="capital-execution-boundary",
            status=OnboardingStatus.READY,
            summary="Broker execution and real-capital behavior remain disabled by ADR-0044.",
        )
    )

    overall = _overall_status(checks)
    return OnboardingReport(
        status=overall,
        storage_root=str(storage_root),
        prepared=prepare and storage_check.status is OnboardingStatus.READY,
        checks=tuple(checks),
        next_commands=_next_commands(storage_root),
    )


def _inspect_storage(storage_root: Path, *, prepare: bool) -> OnboardingCheck:
    try:
        if prepare:
            storage_root.mkdir(parents=True, exist_ok=True)
        if not storage_root.exists():
            return OnboardingCheck(
                check_id="storage-root",
                status=OnboardingStatus.ACTION_REQUIRED,
                summary=f"Storage root does not exist: {storage_root}",
                remediation="Re-run with --prepare to create it.",
            )
        if not storage_root.is_dir():
            return OnboardingCheck(
                check_id="storage-root",
                status=OnboardingStatus.FAILED,
                summary=f"Storage root is not a directory: {storage_root}",
                remediation="Choose a dedicated writable directory.",
            )
        probe = storage_root / ".osca-write-probe"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return OnboardingCheck(
            check_id="storage-root",
            status=OnboardingStatus.FAILED,
            summary=f"Storage root is not writable: {storage_root}",
            remediation=str(exc),
        )
    return OnboardingCheck(
        check_id="storage-root",
        status=OnboardingStatus.READY,
        summary=f"Storage root is writable: {storage_root}",
    )


def _overall_status(checks: list[OnboardingCheck]) -> OnboardingStatus:
    statuses = {check.status for check in checks}
    if OnboardingStatus.FAILED in statuses:
        return OnboardingStatus.FAILED
    if OnboardingStatus.ACTION_REQUIRED in statuses:
        return OnboardingStatus.ACTION_REQUIRED
    return OnboardingStatus.READY


def _next_commands(storage_root: Path) -> tuple[str, ...]:
    root = str(storage_root)
    return (
        "uv run osca readiness",
        (
            "uv run osca local-ohlcv-import "
            "tests/fixtures/local_ohlcv/aapl_backtest_daily.csv AAPL 1d "
            f"--storage-root {root}/local-data"
        ),
        f"uv run python -m osca.analyst_workspace --storage-root {root} --snapshot",
    )
