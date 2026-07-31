from pathlib import Path

from osca.onboarding import OnboardingStatus, inspect_first_run


def test_onboarding_reports_missing_storage_as_action_required(tmp_path: Path) -> None:
    storage_root = tmp_path / "missing"

    report = inspect_first_run(storage_root)

    assert report.status is OnboardingStatus.ACTION_REQUIRED
    assert report.prepared is False
    storage = next(check for check in report.checks if check.check_id == "storage-root")
    assert storage.status is OnboardingStatus.ACTION_REQUIRED
    assert report.network_used is False
    assert report.credentials_used is False
    assert report.real_capital_enabled is False


def test_onboarding_prepares_writable_storage(tmp_path: Path) -> None:
    storage_root = tmp_path / "workspace"

    report = inspect_first_run(storage_root, prepare=True)

    assert storage_root.is_dir()
    assert report.prepared is True
    assert report.status is OnboardingStatus.READY
    assert all(check.status is OnboardingStatus.READY for check in report.checks)
    assert any("local-ohlcv-import" in command for command in report.next_commands)


def test_onboarding_fails_when_storage_is_file(tmp_path: Path) -> None:
    storage_root = tmp_path / "not-a-directory"
    storage_root.write_text("occupied\n", encoding="utf-8")

    report = inspect_first_run(storage_root, prepare=True)

    assert report.status is OnboardingStatus.FAILED
    storage = next(check for check in report.checks if check.check_id == "storage-root")
    assert storage.status is OnboardingStatus.FAILED


def test_onboarding_keeps_execution_boundaries_disabled(tmp_path: Path) -> None:
    report = inspect_first_run(tmp_path, prepare=True)

    assert report.recommendations_enabled is False
    assert report.broker_execution_enabled is False
    assert report.real_capital_enabled is False
    boundary = next(
        check for check in report.checks if check.check_id == "capital-execution-boundary"
    )
    assert "ADR-0044" in boundary.summary
