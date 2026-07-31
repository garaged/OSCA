from __future__ import annotations

import argparse

from osca.runtime_extensions import (
    RuntimePackRequest,
    execute_runtime_pack,
    install_runtime_pack,
    rollback_runtime_pack,
    validate_runtime_pack,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="OSCA governed runtime extension packs")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "install", "run"):
        command = sub.add_parser(name)
        command.add_argument("pack_directory")
        command.add_argument("--storage-root", default=".osca")
        if name == "run":
            command.add_argument("--input", default="{}")
            command.add_argument("--enable", action="store_true")
    rollback = sub.add_parser("rollback")
    rollback.add_argument("package_id")
    rollback.add_argument("target_version")
    rollback.add_argument("--storage-root", default=".osca")

    args = parser.parse_args()
    if args.command == "rollback":
        result = rollback_runtime_pack(
            storage_root=args.storage_root,
            package_id=args.package_id,
            target_version=args.target_version,
        )
    else:
        request = RuntimePackRequest(
            pack_directory=args.pack_directory,
            storage_root=args.storage_root,
            enable_execution=getattr(args, "enable", False),
            input_payload=getattr(args, "input", "{}"),
        )
        if args.command == "validate":
            result = validate_runtime_pack(request)
        elif args.command == "install":
            result = install_runtime_pack(request)
        else:
            result = execute_runtime_pack(request)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
