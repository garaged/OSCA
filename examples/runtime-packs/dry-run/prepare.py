#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import stat
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    executable = root / "run.py"
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    digest = "sha256:" + hashlib.sha256(executable.read_bytes()).hexdigest()
    manifest = {
        "package_id": "osca-dry-run",
        "package_version": "1.0.0",
        "publisher": "garaged",
        "category": "analysis",
        "executable": "run.py",
        "arguments": [],
        "osca_min_version": "0.1.0",
        "trust_tier": "local_trusted",
        "integrity_digest": digest,
        "permissions": [],
        "deterministic": True,
        "max_runtime_seconds": 5,
        "max_output_bytes": 10000,
    }
    manifest_path = root / "osca-pack.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(manifest_path)


if __name__ == "__main__":
    main()
