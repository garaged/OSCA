from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

from scripts import run_desktop


def test_launcher_uses_locked_python_for_sidecar(
    monkeypatch: Any,
) -> None:
    captured: dict[str, Any] = {}

    def fake_run(
        command: list[str],
        *,
        cwd: Path,
        env: dict[str, str],
        check: bool,
    ) -> SimpleNamespace:
        captured.update(command=command, cwd=cwd, env=env, check=check)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(run_desktop.subprocess, "run", fake_run)

    result = run_desktop.main()

    assert result == 0
    assert captured["command"] == ["npm", "run", "tauri", "dev"]
    assert captured["cwd"].name == "desktop"
    assert captured["env"]["OSCA_DESKTOP_PYTHON"] == run_desktop.sys.executable
    assert captured["check"] is False


def test_launcher_reports_missing_desktop_host(monkeypatch: Any) -> None:
    def fail_run(*args: object, **kwargs: object) -> SimpleNamespace:
        del args, kwargs
        raise OSError("npm unavailable")

    monkeypatch.setattr(run_desktop.subprocess, "run", fail_run)

    assert run_desktop.main() == 1
