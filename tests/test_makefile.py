from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"


def test_makefile_exposes_required_desktop_workflows() -> None:
    source = MAKEFILE.read_text(encoding="utf-8")

    for target in (
        "help:",
        "tools:",
        "setup:",
        "run:",
        "acceptance-prepare:",
        "acceptance-reset:",
        "acceptance-run:",
        "acceptance-info:",
        "build:",
        "package:",
        "test:",
        "test-desktop:",
        "lint:",
        "typecheck:",
        "format-check:",
        "check:",
        "clean:",
        "clean-all:",
        "status:",
    ):
        assert target in source


def test_makefile_wraps_canonical_locked_commands() -> None:
    source = MAKEFILE.read_text(encoding="utf-8")

    assert "uv sync --locked" in source or "$(UV) sync --locked" in source
    assert "npm ci" in source or "$(NPM) ci" in source
    assert "scripts/run_desktop.py" in source
    assert "npm run tauri build" in source or "$(NPM) run tauri build" in source
    assert "scripts/contributor_check.py" in source
    assert "cargo clippy" in source or "$(CARGO) clippy" in source


def test_manual_acceptance_is_isolated_and_safe_by_default() -> None:
    source = MAKEFILE.read_text(encoding="utf-8")

    assert "ACCEPTANCE_ROOT ?= $(CURDIR)/.osca/d3-manual-acceptance" in source
    assert 'OSCA_DESKTOP_STATE_ROOT="$(ACCEPTANCE_STATE_ROOT)"' in source
    assert 'rm -rf "$(ACCEPTANCE_ROOT)"' in source
    assert "rm -rf $(HOME)" not in source
    assert "sudo" not in source


def test_makefile_has_no_implicit_network_or_live_execution_target() -> None:
    source = MAKEFILE.read_text(encoding="utf-8").lower()

    assert "network-access-enabled" not in source
    assert "live-order" not in source
    assert "broker" not in source
