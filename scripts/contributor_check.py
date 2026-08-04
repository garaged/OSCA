from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    completed = subprocess.run(command, cwd=ROOT, env=env, check=False)
    if completed.returncode != 0:
        rendered = " ".join(command)
        raise SystemExit(f"contributor validation failed: {rendered}")


def main() -> None:
    environment = dict(os.environ)
    run(["uv", "sync", "--locked"])
    run(["uv", "run", "ruff", "check", "."])
    run(["uv", "run", "mypy"])
    run(["uv", "run", "pytest"], env=environment)
    run(["npm", "ci", "--ignore-scripts"])
    run(["npm", "run", "openspec:doctor"])
    run(["npm", "run", "openspec:validate"])
    run(
        [
            "uv",
            "run",
            "osca",
            "extension",
            "validate",
            "--manifest",
            "examples/extensions/offline-mean/osca-extension.json",
        ]
    )
    print("OSCA contributor validation passed.")


if __name__ == "__main__":
    main()
