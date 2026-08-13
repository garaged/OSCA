"""Build the self-contained Python sidecar bundled with native OSCA desktop packages."""

from __future__ import annotations

import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_ENTRYPOINT = _REPOSITORY_ROOT / "src" / "osca" / "desktop_api" / "stdio.py"
_BUILD_ROOT = _REPOSITORY_ROOT / ".osca" / "desktop-sidecar-build"
_RUNTIME_ROOT = (
    _REPOSITORY_ROOT
    / "apps"
    / "desktop"
    / "src-tauri"
    / "binaries"
    / "osca-sidecar-runtime"
)
_BINARY_NAME = "osca-sidecar"
# Keep package-build smoke validation aligned with the Tauri broker's runtime request budget.
_SMOKE_TIMEOUT_SECONDS = 15.0


def _clear_generated_runtime() -> None:
    _RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    for child in _RUNTIME_ROOT.iterdir():
        if child.name == ".gitignore":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def _smoke_sidecar(executable: Path) -> None:
    request = (
        '{"protocol_version":"1.0","request_id":"package-smoke",'
        '"method":"desktop.bootstrap","params":{}}\n'
    )
    for attempt in range(2):
        started = time.monotonic()
        try:
            completed = subprocess.run(
                [str(executable)],
                input=request,
                capture_output=True,
                text=True,
                timeout=_SMOKE_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"packaged sidecar smoke attempt {attempt + 1} exceeded "
                f"the {_SMOKE_TIMEOUT_SECONDS:.0f}s desktop broker request budget"
            ) from exc
        elapsed = time.monotonic() - started
        if completed.returncode != 0:
            raise RuntimeError(
                f"packaged sidecar smoke attempt {attempt + 1} failed: "
                f"{completed.stderr.strip()}"
            )
        if '"status":"ok"' not in completed.stdout:
            raise RuntimeError(
                f"packaged sidecar smoke attempt {attempt + 1} returned an invalid response"
            )
        print(f"Desktop sidecar cold-start smoke {attempt + 1}: {elapsed:.3f}s")


def main() -> int:
    shutil.rmtree(_BUILD_ROOT, ignore_errors=True)
    dist_root = _BUILD_ROOT / "dist"
    work_root = _BUILD_ROOT / "work"
    spec_root = _BUILD_ROOT / "spec"
    dist_root.mkdir(parents=True, exist_ok=True)
    work_root.mkdir(parents=True, exist_ok=True)
    spec_root.mkdir(parents=True, exist_ok=True)
    _clear_generated_runtime()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onedir",
            "--name",
            _BINARY_NAME,
            "--paths",
            str(_REPOSITORY_ROOT / "src"),
            "--collect-submodules",
            "osca",
            "--collect-data",
            "osca",
            "--distpath",
            str(dist_root),
            "--workpath",
            str(work_root),
            "--specpath",
            str(spec_root),
            str(_ENTRYPOINT),
        ],
        cwd=_REPOSITORY_ROOT,
        check=True,
    )

    built_runtime = dist_root / _BINARY_NAME
    built_executable = built_runtime / _BINARY_NAME
    if not built_executable.is_file():
        raise FileNotFoundError(f"PyInstaller did not produce {built_executable}")

    for child in built_runtime.iterdir():
        destination = _RUNTIME_ROOT / child.name
        if child.is_dir():
            shutil.copytree(child, destination)
        else:
            shutil.copy2(child, destination)

    executable = _RUNTIME_ROOT / _BINARY_NAME
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    _smoke_sidecar(executable)
    print(f"Desktop sidecar runtime: {_RUNTIME_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
