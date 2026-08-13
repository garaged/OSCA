from __future__ import annotations

import json
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_tauri_bundle_declares_self_contained_sidecar_runtime() -> None:
    config = json.loads(
        (_REPOSITORY_ROOT / "apps" / "desktop" / "src-tauri" / "tauri.conf.json").read_text()
    )
    assert config["bundle"]["resources"] == ["binaries/osca-sidecar-runtime"]
    assert "externalBin" not in config["bundle"]
    assert "npm run build:sidecar" in config["build"]["beforeBuildCommand"]


def test_sidecar_build_is_pinned_onedir_and_performance_smoked() -> None:
    package = json.loads((_REPOSITORY_ROOT / "apps" / "desktop" / "package.json").read_text())
    command = package["scripts"]["build:sidecar"]
    assert "pyinstaller==6.15.0" in command
    assert "scripts/build_desktop_sidecar.py" in command

    source = (_REPOSITORY_ROOT / "scripts" / "build_desktop_sidecar.py").read_text()
    assert '"--onedir"' in source
    assert '"--onefile"' not in source
    assert "osca-sidecar-runtime" in source
    assert "_SMOKE_TIMEOUT_SECONDS = 5.0" in source
    assert "for attempt in range(2)" in source
    assert '"--collect-submodules"' in source
    assert '"osca"' in source


def test_native_broker_prefers_resource_sidecar_outside_development() -> None:
    source = (
        _REPOSITORY_ROOT / "apps" / "desktop" / "src-tauri" / "src" / "lib.rs"
    ).read_text()
    assert "bundled_sidecar_path(window.app_handle())" in source
    assert "app.path().resource_dir()" in source
    assert 'join("osca-sidecar-runtime")' in source
    assert "packaged_sidecar_is_resolved_from_resource_runtime" in source
    assert "bundled_sidecar_is_used_without_development_overrides" in source
    assert "default_sidecar_uses_python3_module_execution_as_last_resort" in source
