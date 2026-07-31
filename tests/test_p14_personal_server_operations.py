from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from osca.personal_server import (
    AlertRequest,
    AlertTransport,
    BackupRequest,
    OperationsStatus,
    PersonalServerSecurity,
    RestoreRequest,
    ScheduledJob,
    create_backup,
    deliver_alert,
    restore_backup,
    run_scheduled_job,
)


def test_non_loopback_requires_tls_and_authentication() -> None:
    with pytest.raises(ValidationError, match="requires TLS and authentication"):
        PersonalServerSecurity(bind_host="0.0.0.0")

    config = PersonalServerSecurity(
        bind_host="0.0.0.0",
        tls_enabled=True,
        authentication_enabled=True,
    )
    assert config.session_cookie_secure


def test_scheduled_job_is_blocked_until_explicitly_enabled(tmp_path: Path) -> None:
    evidence = run_scheduled_job(
        ScheduledJob(job_id="health", command=(sys.executable, "--version")),
        evidence_root=str(tmp_path),
    )
    assert evidence.status is OperationsStatus.POLICY_BLOCKED
    assert evidence.findings == ("job-not-enabled",)


def test_scheduled_job_retains_stdout_and_stderr(tmp_path: Path) -> None:
    evidence = run_scheduled_job(
        ScheduledJob(
            job_id="echo",
            command=(sys.executable, "-c", "print('ok')"),
            enabled=True,
        ),
        evidence_root=str(tmp_path),
    )
    assert evidence.status is OperationsStatus.SUCCEEDED
    assert evidence.exit_code == 0
    assert evidence.stdout_uri is not None
    assert Path(evidence.stdout_uri.removeprefix("file://")).read_text().strip() == "ok"


def test_file_alert_requires_enablement_and_appends_json(tmp_path: Path) -> None:
    destination = tmp_path / "alerts.jsonl"
    blocked = deliver_alert(
        AlertRequest(
            transport=AlertTransport.FILE,
            subject="job-failed",
            message="A governed job failed.",
            destination=str(destination),
        )
    )
    assert blocked.status is OperationsStatus.POLICY_BLOCKED
    assert not destination.exists()

    delivered = deliver_alert(
        AlertRequest(
            transport=AlertTransport.FILE,
            subject="job-failed",
            message="A governed job failed.",
            destination=str(destination),
            enabled=True,
        )
    )
    assert delivered.status is OperationsStatus.SUCCEEDED
    payload = json.loads(destination.read_text().splitlines()[0])
    assert payload["subject"] == "job-failed"


def test_webhook_requires_https() -> None:
    with pytest.raises(ValidationError, match="HTTPS"):
        AlertRequest(
            transport=AlertTransport.WEBHOOK,
            subject="warning",
            message="test",
            destination="http://example.test/hook",
        )


def test_backup_requires_off_source_destination_and_restores(tmp_path: Path) -> None:
    source = tmp_path / "source"
    state = source / "state"
    state.mkdir(parents=True)
    (state / "osca.db").write_text("state", encoding="utf-8")

    inside = create_backup(
        BackupRequest(
            source_root=str(source),
            destination_root=str(source / "backups"),
            enabled=True,
        )
    )
    assert inside.status is OperationsStatus.POLICY_BLOCKED

    backup_root = tmp_path / "off-device"
    backup = create_backup(
        BackupRequest(
            source_root=str(source),
            destination_root=str(backup_root),
            enabled=True,
        )
    )
    assert backup.status is OperationsStatus.SUCCEEDED
    assert backup.archive_uri is not None
    assert backup.sha256 is not None

    restore_root = tmp_path / "restore"
    restored = restore_backup(
        RestoreRequest(
            archive_path=backup.archive_uri.removeprefix("file://"),
            destination_root=str(restore_root),
            enabled=True,
        )
    )
    assert restored.status is OperationsStatus.SUCCEEDED
    assert (restore_root / "state" / "osca.db").read_text() == "state"


def test_restore_requires_explicit_enablement(tmp_path: Path) -> None:
    evidence = restore_backup(
        RestoreRequest(
            archive_path=str(tmp_path / "missing.tar.gz"),
            destination_root=str(tmp_path / "restore"),
        )
    )
    assert evidence.status is OperationsStatus.POLICY_BLOCKED


def test_restore_blocks_nonempty_destination_without_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "source"
    (source / "state").mkdir(parents=True)
    (source / "state" / "osca.db").write_text("state")
    backup = create_backup(
        BackupRequest(
            source_root=str(source),
            destination_root=str(tmp_path / "backup"),
            enabled=True,
        )
    )
    destination = tmp_path / "restore"
    destination.mkdir()
    (destination / "existing").write_text("keep")
    assert backup.archive_uri is not None
    evidence = restore_backup(
        RestoreRequest(
            archive_path=backup.archive_uri.removeprefix("file://"),
            destination_root=str(destination),
            enabled=True,
        )
    )
    assert evidence.status is OperationsStatus.POLICY_BLOCKED
    assert evidence.findings == ("overwrite-not-enabled",)
