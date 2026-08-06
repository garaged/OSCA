"""Launch the D2 desktop host with the locked OSCA Python interpreter."""

from __future__ import annotations

import os
import subprocess
import sys
from importlib import import_module
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_DESKTOP_ROOT = _REPOSITORY_ROOT / "apps" / "desktop"
_SUPPORTED_PYTHON = (3, 13)


def main() -> int:
    """Run Tauri development mode with the current Python as the sidecar interpreter."""

    if sys.version_info[:2] != _SUPPORTED_PYTHON:
        detected = f"{sys.version_info.major}.{sys.version_info.minor}"
        print(
            f"OSCA desktop development requires Python 3.13; detected {detected}.",
            file=sys.stderr,
        )
        return 2

    try:
        import_module("osca.desktop_api")
    except ImportError as exc:
        print(
            "The OSCA package is unavailable in this Python environment. "
            "Run 'uv sync --locked' first.",
            file=sys.stderr,
        )
        print(str(exc), file=sys.stderr)
        return 2

    environment = os.environ.copy()
    environment["OSCA_DESKTOP_PYTHON"] = sys.executable
    try:
        completed = subprocess.run(
            ["npm", "run", "tauri", "dev"],
            cwd=_DESKTOP_ROOT,
            env=environment,
            check=False,
        )
    except OSError as exc:
        print(f"Unable to start the OSCA desktop development host: {exc}", file=sys.stderr)
        return 1
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
