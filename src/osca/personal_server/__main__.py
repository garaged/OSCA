from __future__ import annotations

import argparse
import json
from pathlib import Path

from osca.personal_server import (
    AlertRequest,
    AlertTransport,
    BackupRequest,
    PersonalServerSecurity,
    RestoreRequest,
    ScheduledJob,
    create_backup,
    deliver_alert,
    restore_backup,
    run_scheduled_job,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="OSCA personal-server operations")
    sub = parser.add_subparsers(dest="command", required=True)

    security = sub.add_parser("security-check")
    security.add_argument("--host", default="127.0.0.1")
    security.add_argument("--tls", action="store_true")
    security.add_argument("--auth", action="store_true")

    run = sub.add_parser("run-job")
    run.add_argument("--job-id", required=True)
    run.add_argument("--evidence-root", required=True)
    run.add_argument("--working-directory", default=".")
    run.add_argument("--enable", action="store_true")
    run.add_argument("job_command", nargs=argparse.REMAINDER)

    alert = sub.add_parser("alert-file")
    alert.add_argument("--destination", required=True)
    alert.add_argument("--subject", required=True)
    alert.add_argument("--message", required=True)
    alert.add_argument("--enable", action="store_true")

    backup = sub.add_parser("backup")
    backup.add_argument("--source-root", required=True)
    backup.add_argument("--destination-root", required=True)
    backup.add_argument("--enable", action="store_true")

    restore = sub.add_parser("restore")
    restore.add_argument("--archive", required=True)
    restore.add_argument("--destination-root", required=True)
    restore.add_argument("--enable", action="store_true")
    restore.add_argument("--overwrite", action="store_true")

    args = parser.parse_args()
    if args.command == "security-check":
        result = PersonalServerSecurity(
            bind_host=args.host,
            tls_enabled=args.tls,
            authentication_enabled=args.auth,
        )
        print(result.model_dump_json(indent=2))
    elif args.command == "run-job":
        command = tuple(args.job_command)
        if not command:
            parser.error("run-job requires a command after --")
        result = run_scheduled_job(
            ScheduledJob(
                job_id=args.job_id,
                command=command,
                enabled=args.enable,
                working_directory=args.working_directory,
            ),
            evidence_root=args.evidence_root,
        )
        print(result.model_dump_json(indent=2))
    elif args.command == "alert-file":
        result = deliver_alert(
            AlertRequest(
                transport=AlertTransport.FILE,
                subject=args.subject,
                message=args.message,
                destination=args.destination,
                enabled=args.enable,
            )
        )
        print(result.model_dump_json(indent=2))
    elif args.command == "backup":
        result = create_backup(
            BackupRequest(
                source_root=args.source_root,
                destination_root=args.destination_root,
                enabled=args.enable,
            )
        )
        print(result.model_dump_json(indent=2))
    else:
        result = restore_backup(
            RestoreRequest(
                archive_path=args.archive,
                destination_root=args.destination_root,
                enabled=args.enable,
                overwrite=args.overwrite,
            )
        )
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
