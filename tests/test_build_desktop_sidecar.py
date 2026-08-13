from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest

from scripts import build_desktop_sidecar


def test_smoke_sidecar_uses_desktop_broker_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
        calls.append(kwargs)
        return SimpleNamespace(returncode=0, stdout='{"status":"ok"}\n', stderr="")

    monkeypatch.setattr(build_desktop_sidecar.subprocess, "run", fake_run)

    build_desktop_sidecar._smoke_sidecar(Path("/tmp/osca-sidecar"))

    assert len(calls) == 2
    assert all(call["timeout"] == 15.0 for call in calls)


def test_smoke_sidecar_reports_broker_budget_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*args: object, **kwargs: object) -> SimpleNamespace:
        raise subprocess.TimeoutExpired(cmd=["/tmp/osca-sidecar"], timeout=15.0)

    monkeypatch.setattr(build_desktop_sidecar.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="exceeded the 15s desktop broker request budget"):
        build_desktop_sidecar._smoke_sidecar(Path("/tmp/osca-sidecar"))
