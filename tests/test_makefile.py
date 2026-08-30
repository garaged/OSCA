from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"


def test_makefile_exposes_required_desktop_workflows() -> None:
    source = MAKEFILE.read_text(encoding="utf-8")

    for target in (
        "help:",
        "tools:",
        "setup:",
        "run:",
        "run-clean:",
        "acceptance-prepare:",
        "acceptance-reset:",
        "acceptance-seed:",
        "acceptance-run:",
        "acceptance-check:",
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
    assert "$(NPM) run tauri -- build" in source
    assert "scripts/contributor_check.py" in source
    assert "cargo clippy" in source or "$(CARGO) clippy" in source


def test_makefile_builds_only_platform_native_acceptance_bundle() -> None:
    source = MAKEFILE.read_text(encoding="utf-8")

    assert '"$$(uname -s)" = "Darwin"' in source
    assert "$(NPM) run tauri -- build --bundles app" in source
    assert '"$$(uname -s)" = "Linux"' in source
    assert "$(NPM) run tauri -- build --bundles deb" in source


def test_makefile_help_and_build_dry_run_parse() -> None:
    help_result = subprocess.run(
        ["make", "help"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "make build" in help_result.stdout
    assert "make run-clean" in help_result.stdout
    assert "make acceptance-check" in help_result.stdout

    dry_run = subprocess.run(
        ["make", "-n", "build"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "npm run tauri -- build --bundles app" in dry_run.stdout
    assert "npm run tauri -- build --bundles deb" in dry_run.stdout


def test_manual_acceptance_is_isolated_and_safe_by_default() -> None:
    source = MAKEFILE.read_text(encoding="utf-8")

    assert "ACCEPTANCE_ROOT ?= $(CURDIR)/.osca/desktop-acceptance" in source
    assert "scripts/prepare_desktop_acceptance.py" in source
    assert 'OSCA_DESKTOP_STATE_ROOT="$(ACCEPTANCE_STATE_ROOT)"' in source
    assert 'scripts/prepare_desktop_acceptance.py --root "$(ACCEPTANCE_ROOT)" --reset' in source
    assert "rm -rf $(HOME)" not in source
    assert "sudo" not in source


def test_focused_desktop_suite_advances_through_d8() -> None:
    source = MAKEFILE.read_text(encoding="utf-8")

    assert "tests/test_d3_desktop_*.py" in source
    assert "tests/test_d4_*.py" in source
    assert "tests/test_d5_*.py" in source
    assert "tests/test_d6_*.py" in source
    assert "tests/test_d7_*.py" in source
    assert "tests/test_d8_*.py" in source
    assert "tests/test_desktop_acceptance_prepare.py" in source
    assert "tests/test_desktop_packaging.py" in source


def test_makefile_has_no_implicit_network_or_live_execution_target() -> None:
    source = MAKEFILE.read_text(encoding="utf-8").lower()
    target_lines = [
        line
        for line in source.splitlines()
        if line and not line.startswith(("\t", " "))
    ]
    declarations = "\n".join(target_lines)

    assert "network-access-enabled" not in source
    assert "live-order" not in source
    assert "network:" not in declarations
    assert "live:" not in declarations
    assert "execute:" not in declarations
