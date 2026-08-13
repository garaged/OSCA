"""Build the self-contained Python sidecar bundled with native OSCA desktop packages."""

from __future__ import annotations

import shutil
import stat
import subprocess
import sys
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_ENTRYPOINT = _REPOSITORY_ROOT / "src" / "osca" / "desktop_api" / "stdio.py"
_BUILD_ROOT = _REPOSITORY_ROOT / ".osca" / "desktop-sidecar-build"
_BINARY_ROOT = _REPOSITORY_ROOT / "apps" / "desktop" / "src-tauri" / "binaries"
_BINARY_NAME = "osca-sidecar"


def _rust_target_triple() -> str:
    completed = subprocess.run(
        ["rustc", "-vV"],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in completed.stdout.splitlines():
        if line.startswith("host: "):
            return line.removeprefix("host: ").strip()
    raise RuntimeError("rustc -vV did not report a host target triple")


def main() -> int:
    target = _rust_target_triple()
    shutil.rmtree(_BUILD_ROOT, ignore_errors=True)
    dist_root = _BUILD_ROOT / "dist"
    work_root = _BUILD_ROOT / "work"
    spec_root = _BUILD_ROOT / "spec"
    dist_root.mkdir(parents=True, exist_ok=True)
    work_root.mkdir(parents=True, exist_ok=True)
    spec_root.mkdir(parents=True, exist_ok=True)
    _BINARY_ROOT.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--onefile",
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

    built = dist_root / _BINARY_NAME
    if not built.is_file():
        raise FileNotFoundError(f"PyInstaller did not produce {built}")
    destination = _BINARY_ROOT / f"{_BINARY_NAME}-{target}"
    shutil.copy2(built, destination)
    destination.chmod(destination.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"Desktop sidecar: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
