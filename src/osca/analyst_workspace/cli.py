from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import cast

import uvicorn

from osca.analyst_workspace.app import create_app
from osca.analyst_workspace.services import AnalystWorkspaceService

_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m osca.analyst_workspace",
        description="Inspect retained OSCA evidence through a read-only local workspace.",
    )
    parser.add_argument("--storage-root", type=Path, default=Path(".osca"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Print the read-only workspace snapshot as JSON and exit.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    storage_root = cast(Path, args.storage_root)
    host = cast(str, args.host)
    port = cast(int, args.port)
    if port < 1 or port > 65535:
        print(json.dumps({"error": "port must be between 1 and 65535"}), file=sys.stderr)
        return 2
    if cast(bool, args.snapshot):
        snapshot = AnalystWorkspaceService().snapshot(storage_root)
        print(json.dumps(snapshot.model_dump(mode="json"), indent=2, sort_keys=True))
        return 0
    if host not in _LOOPBACK_HOSTS:
        print(
            json.dumps(
                {
                    "error": (
                        "P11 workspace binds only to loopback hosts; use 127.0.0.1, "
                        "localhost, or ::1"
                    )
                }
            ),
            file=sys.stderr,
        )
        return 2
    uvicorn.run(create_app(storage_root=storage_root), host=host, port=port)
    return 0
