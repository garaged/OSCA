from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.service import DesktopApplicationService


def _request(
    service: DesktopApplicationService,
    method: str,
    params: dict[str, Any] | None = None,
) -> DesktopResponse:
    return service.handle(
        DesktopRequest(
            request_id=f"test-{method}",
            method=method,
            params=params or {},
        )
    )


def _create_profile(service: DesktopApplicationService, profile_root: Path) -> None:
    profile_root.parent.mkdir(parents=True, exist_ok=True)
    response = _request(
        service,
        "profile.create",
        {"profile_root": str(profile_root)},
    )
    assert response.status == "ok", response.error


def test_bootstrap_is_first_run_and_financial_capabilities_fail_closed(tmp_path: Path) -> None:
    service = DesktopApplicationService(state_root=tmp_path / "desktop-state")

    response = _request(service, "desktop.bootstrap")

    assert response.status == "ok"
    assert response.result is not None
    assert response.result["first_run_required"] is True
    capabilities = response.result["capabilities"]
    assert capabilities["profile_management"] is True
    assert capabilities["bundled_sample_import"] is True
    assert capabilities["provider_setup"] is False
    assert capabilities["recommendations"] is False
    assert capabilities["broker_connectivity"] is False
    assert capabilities["live_order_execution"] is False
    disclosures = response.result["disclosures"]
    assert "not financial advice" in disclosures["research_only"]
    assert "disabled" in disclosures["live_execution"]


def test_create_select_open_and_list_profile_through_authoritative_services(
    tmp_path: Path,
) -> None:
    profile_root = tmp_path / "profiles" / "primary"
    state_root = tmp_path / "desktop-state"
    service = DesktopApplicationService(state_root=state_root)

    _create_profile(service, profile_root)

    assert (profile_root / "config.json").is_file()
    created_bootstrap = _request(service, "desktop.bootstrap")
    assert created_bootstrap.status == "ok"
    assert created_bootstrap.result is not None
    assert created_bootstrap.result["first_run_required"] is False
    assert created_bootstrap.result["selected_profile"] == str(profile_root.resolve())

    selected = _request(
        service,
        "profile.select",
        {"profile_root": str(profile_root)},
    )
    assert selected.status == "ok"
    assert selected.result is not None
    assert selected.result["profile"]["can_open"] is True

    opened = _request(
        service,
        "profile.open",
        {"profile_root": str(profile_root)},
    )
    assert opened.status == "ok"
    assert opened.result is not None
    assert opened.result["status"] == "opened"
    assert opened.result["diagnostics"]["status"] in {"ready", "warning"}

    profiles = _request(service, "profile.list")
    assert profiles.status == "ok"
    assert profiles.result is not None
    assert len(profiles.result["profiles"]) == 1
    assert profiles.result["profiles"][0]["path"] == str(profile_root.resolve())
    assert profiles.result["profiles"][0]["last_opened_at"] is not None


def test_profile_create_rejects_non_empty_target_without_mutation(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles" / "occupied"
    profile_root.mkdir(parents=True)
    sentinel = profile_root / "keep.txt"
    sentinel.write_text("do not replace", encoding="utf-8")
    service = DesktopApplicationService(state_root=tmp_path / "desktop-state")

    response = _request(
        service,
        "profile.create",
        {"profile_root": str(profile_root)},
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "unsafe_profile_target"
    assert sentinel.read_text(encoding="utf-8") == "do not replace"
    assert not (profile_root / "config.json").exists()


def test_profile_create_restores_initially_empty_target_after_partial_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile_root = tmp_path / "profiles" / "empty-target"
    profile_root.mkdir(parents=True)
    service = DesktopApplicationService(state_root=tmp_path / "desktop-state")

    def fail_after_partial_write(
        root: Path,
        *,
        storage_root: Path | None = None,
        workspace_port: int = 8765,
    ) -> dict[str, object]:
        assert storage_root is None
        assert workspace_port == 8765
        (root / "data").mkdir(parents=True)
        (root / "config.json").write_text("partial", encoding="utf-8")
        raise OSError("simulated initialization failure")

    monkeypatch.setattr(
        "osca.desktop_api.service.initialize_profile",
        fail_after_partial_write,
    )

    response = _request(
        service,
        "profile.create",
        {"profile_root": str(profile_root)},
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "application_error"
    assert profile_root.is_dir()
    assert tuple(profile_root.iterdir()) == ()
    bootstrap = _request(service, "desktop.bootstrap")
    assert bootstrap.result is not None
    assert bootstrap.result["first_run_required"] is True


def test_profile_create_does_not_record_open_state_before_final_inspection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile_root = tmp_path / "profiles" / "inspection-failure"
    profile_root.parent.mkdir(parents=True)
    service = DesktopApplicationService(state_root=tmp_path / "desktop-state")

    def fail_inspection(_: Path) -> dict[str, Any]:
        raise OSError("simulated final inspection failure")

    monkeypatch.setattr(service, "_inspect_profile", fail_inspection)

    response = _request(
        service,
        "profile.create",
        {"profile_root": str(profile_root)},
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "application_error"
    assert (profile_root / "config.json").is_file()
    bootstrap = _request(service, "desktop.bootstrap")
    assert bootstrap.result is not None
    assert bootstrap.result["first_run_required"] is True
    assert bootstrap.result["selected_profile"] is None


def test_profile_inspection_does_not_create_missing_profile(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles" / "missing"
    profile_root.parent.mkdir(parents=True)
    service = DesktopApplicationService(state_root=tmp_path / "desktop-state")

    response = _request(
        service,
        "profile.inspect",
        {"profile_root": str(profile_root)},
    )

    assert response.status == "ok"
    assert response.result is not None
    assert response.result["exists"] is False
    assert response.result["can_open"] is False
    assert not profile_root.exists()


def test_profile_open_fails_closed_during_lock_contention(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles" / "locked"
    service = DesktopApplicationService(state_root=tmp_path / "desktop-state")
    _create_profile(service, profile_root)

    with ProfileMutationLock(profile_root):
        response = _request(
            service,
            "profile.open",
            {"profile_root": str(profile_root)},
        )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "profile_locked"


def test_bundled_sample_import_is_offline_synthetic_and_idempotent(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles" / "sample"
    service = DesktopApplicationService(state_root=tmp_path / "desktop-state")
    _create_profile(service, profile_root)

    first = _request(
        service,
        "sample.import",
        {"profile_root": str(profile_root)},
    )
    second = _request(
        service,
        "sample.import",
        {"profile_root": str(profile_root)},
    )

    assert first.status == "ok", first.error
    assert second.status == "ok", second.error
    assert first.result is not None
    assert second.result is not None
    assert first.result["synthetic"] is True
    assert first.result["network_access_enabled"] is False
    assert first.result["provider_account_required"] is False
    assert first.result["credential_required"] is False
    assert first.result["import"]["symbol"] == "AAPL-SYNTHETIC"
    assert first.result["import"]["network_access_enabled"] is False
    assert (
        first.result["import"]["dataset_revision_id"]
        == second.result["import"]["dataset_revision_id"]
    )
    assert Path(first.result["import"]["payload_uri"]).is_file()
    assert Path(first.result["import"]["metadata_uri"]).is_file()


def test_relative_profile_paths_fail_at_the_desktop_boundary(tmp_path: Path) -> None:
    service = DesktopApplicationService(state_root=tmp_path / "desktop-state")

    response = _request(
        service,
        "profile.inspect",
        {"profile_root": "relative/profile"},
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "invalid_parameters"


def test_diagnostics_report_explicit_disabled_boundaries(tmp_path: Path) -> None:
    service = DesktopApplicationService(state_root=tmp_path / "desktop-state")

    response = _request(service, "system.diagnostics")

    assert response.status == "ok"
    assert response.result is not None
    assert response.result["network_policy"].startswith("disabled")
    assert response.result["recommendations_enabled"] is False
    assert response.result["live_execution_enabled"] is False
