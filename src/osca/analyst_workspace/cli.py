from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import cast

import uvicorn

from osca.analyst_workspace.app import create_app
from osca.analyst_workspace.contracts import (
    WorkspaceFilter,
    WorkspaceItemStatus,
    WorkspaceSection,
)
from osca.analyst_workspace.evidence import WorkspaceEvidenceService

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
    parser.add_argument("--section", choices=[item.value for item in WorkspaceSection])
    parser.add_argument("--status", choices=[item.value for item in WorkspaceItemStatus])
    parser.add_argument("--symbol")
    parser.add_argument("--timeframe")
    parser.add_argument("--detail-item", help="Print one evidence detail contract as JSON.")
    parser.add_argument("--export-item", help="Create one governed portable evidence ZIP.")
    parser.add_argument("--output", type=Path, help="Output path for --export-item.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    storage_root = cast(Path, args.storage_root)
    host = cast(str, args.host)
    port = cast(int, args.port)
    evidence = WorkspaceEvidenceService()
    if port < 1 or port > 65535:
        print(json.dumps({"error": "port must be between 1 and 65535"}), file=sys.stderr)
        return 2
    try:
        if cast(str | None, args.detail_item):
            detail = evidence.detail(storage_root, cast(str, args.detail_item))
            print(json.dumps(detail.model_dump(mode="json"), indent=2, sort_keys=True))
            return 0
        if cast(str | None, args.export_item):
            output = cast(Path | None, args.output)
            if output is None:
                message = {"error": "--output is required with --export-item"}
                print(json.dumps(message), file=sys.stderr)
                return 2
            payload = evidence.portable_export(storage_root, cast(str, args.export_item))
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(payload)
            print(json.dumps({"output": str(output), "size_bytes": len(payload)}))
            return 0
        if cast(bool, args.snapshot):
            snapshot = evidence.filtered_snapshot(
                storage_root,
                WorkspaceFilter(
                    section=(
                        WorkspaceSection(cast(str, args.section)) if args.section else None
                    ),
                    status=(
                        WorkspaceItemStatus(cast(str, args.status)) if args.status else None
                    ),
                    symbol=cast(str | None, args.symbol),
                    timeframe=cast(str | None, args.timeframe),
                ),
            )
            print(json.dumps(snapshot.model_dump(mode="json"), indent=2, sort_keys=True))
            return 0
    except (KeyError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
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
