from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tarfile
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from osca.personal_server.contracts import (
    AlertEvidence,
    AlertRequest,
    AlertTransport,
    BackupEvidence,
    BackupRequest,
    JobRunEvidence,
    OperationsStatus,
    RestoreEvidence,
    RestoreRequest,
    ScheduledJob,
)

WebhookTransport = Callable[[AlertRequest], None]


def run_scheduled_job(job: ScheduledJob, *, evidence_root: str) -> JobRunEvidence:
    if not job.enabled:
        return JobRunEvidence(
            job_id=job.job_id,
            status=OperationsStatus.POLICY_BLOCKED,
            rationale="Scheduled job execution requires explicit enablement.",
            findings=("job-not-enabled",),
        )
    root = Path(evidence_root).resolve() / "personal-server" / "jobs" / job.job_id
    root.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC)
    try:
        completed = subprocess.run(
            job.command,
            cwd=Path(job.working_directory).resolve(),
            capture_output=True,
            check=False,
            text=True,
            timeout=job.timeout_seconds,
        )
        status = (
            OperationsStatus.SUCCEEDED
            if completed.returncode == 0
            else OperationsStatus.FAILED
        )
        stdout_path = root / f"{started.timestamp():.0f}.stdout.log"
        stderr_path = root / f"{started.timestamp():.0f}.stderr.log"
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        return JobRunEvidence(
            job_id=job.job_id,
            status=status,
            exit_code=completed.returncode,
            started_at=started,
            finished_at=datetime.now(UTC),
            stdout_uri=stdout_path.as_uri(),
            stderr_uri=stderr_path.as_uri(),
            rationale="Governed scheduled command completed.",
            findings=() if completed.returncode == 0 else ("non-zero-exit",),
        )
    except subprocess.TimeoutExpired:
        return JobRunEvidence(
            job_id=job.job_id,
            status=OperationsStatus.FAILED,
            started_at=started,
            finished_at=datetime.now(UTC),
            rationale="Governed scheduled command exceeded its timeout.",
            findings=("job-timeout",),
        )


def deliver_alert(
    request: AlertRequest,
    *,
    transport: WebhookTransport | None = None,
) -> AlertEvidence:
    if not request.enabled:
        return _alert_evidence(
            request,
            OperationsStatus.POLICY_BLOCKED,
            "External alert delivery requires explicit enablement.",
            ("alert-not-enabled",),
        )
    try:
        if request.transport is AlertTransport.FILE:
            path = Path(request.destination).resolve()
            path.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "subject": request.subject,
                "message": request.message,
                "created_at": datetime.now(UTC).isoformat(),
            }
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
        else:
            (transport or _webhook_transport)(request)
    except OSError as exc:
        return _alert_evidence(
            request,
            OperationsStatus.FAILED,
            "Alert delivery failed.",
            ("alert-delivery-failed", type(exc).__name__),
        )
    return _alert_evidence(
        request,
        OperationsStatus.SUCCEEDED,
        "Alert delivered through the explicitly configured transport.",
    )


def create_backup(request: BackupRequest) -> BackupEvidence:
    if not request.enabled:
        return BackupEvidence(
            status=OperationsStatus.POLICY_BLOCKED,
            rationale="Off-device backup requires explicit enablement.",
            findings=("backup-not-enabled",),
        )
    source = Path(request.source_root).resolve()
    destination = Path(request.destination_root).resolve()
    if destination == source or source in destination.parents:
        return BackupEvidence(
            status=OperationsStatus.POLICY_BLOCKED,
            rationale="Backup destination must be outside the source tree.",
            findings=("destination-not-off-device",),
        )
    selected: list[Path] = []
    for relative in request.include_paths:
        path = source / relative
        if path.exists():
            selected.append(path)
    if not selected:
        return BackupEvidence(
            status=OperationsStatus.FAILED,
            rationale="No requested backup paths exist.",
            findings=("backup-source-empty",),
        )
    destination.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    archive = destination / f"osca-backup-{timestamp}.tar.gz"
    manifest = destination / f"osca-backup-{timestamp}.manifest.json"
    with tarfile.open(archive, "w:gz") as handle:
        for path in selected:
            handle.add(path, arcname=path.relative_to(source))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    file_count = sum(1 for path in selected for item in path.rglob("*") if item.is_file())
    manifest.write_text(
        json.dumps(
            {
                "archive": archive.name,
                "sha256": f"sha256:{digest}",
                "file_count": file_count,
                "include_paths": request.include_paths,
                "created_at": datetime.now(UTC).isoformat(),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return BackupEvidence(
        status=OperationsStatus.SUCCEEDED,
        archive_uri=archive.as_uri(),
        manifest_uri=manifest.as_uri(),
        sha256=f"sha256:{digest}",
        file_count=file_count,
        rationale="Backup archive and manifest created outside the source tree.",
        findings=("restore-verification-required",),
    )


def restore_backup(request: RestoreRequest) -> RestoreEvidence:
    if not request.enabled:
        return RestoreEvidence(
            status=OperationsStatus.POLICY_BLOCKED,
            rationale="Restore execution requires explicit enablement.",
            findings=("restore-not-enabled",),
        )
    archive = Path(request.archive_path).resolve()
    destination = Path(request.destination_root).resolve()
    if not archive.is_file():
        return RestoreEvidence(
            status=OperationsStatus.FAILED,
            rationale="Backup archive does not exist.",
            findings=("archive-missing",),
        )
    if destination.exists() and any(destination.iterdir()) and not request.overwrite:
        return RestoreEvidence(
            status=OperationsStatus.POLICY_BLOCKED,
            rationale="Non-empty restore destination requires explicit overwrite permission.",
            findings=("overwrite-not-enabled",),
        )
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="osca-restore-") as temporary:
        staging = Path(temporary)
        try:
            with tarfile.open(archive, "r:gz") as handle:
                members = handle.getmembers()
                for member in members:
                    target = (staging / member.name).resolve()
                    if staging.resolve() not in target.parents and target != staging.resolve():
                        raise ValueError("archive contains an unsafe path")
                handle.extractall(staging, filter="data")
        except (tarfile.TarError, ValueError):
            return RestoreEvidence(
                status=OperationsStatus.FAILED,
                rationale="Backup archive failed integrity or path-safety validation.",
                findings=("archive-validation-failed",),
            )
        if request.overwrite:
            for child in destination.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        restored = 0
        for child in staging.iterdir():
            target = destination / child.name
            if child.is_dir():
                shutil.copytree(child, target, dirs_exist_ok=request.overwrite)
                restored += sum(1 for item in child.rglob("*") if item.is_file())
            else:
                shutil.copy2(child, target)
                restored += 1
    return RestoreEvidence(
        status=OperationsStatus.SUCCEEDED,
        restored_file_count=restored,
        destination_uri=destination.as_uri(),
        rationale="Backup restored through a validated staging directory.",
        findings=("operator-post-restore-validation-required",),
    )


def _webhook_transport(request: AlertRequest) -> None:
    payload = json.dumps(
        {"subject": request.subject, "message": request.message}
    ).encode("utf-8")
    http_request = urllib.request.Request(
        request.destination,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(http_request, timeout=request.timeout_seconds) as response:
            if not 200 <= response.status < 300:
                raise OSError(f"webhook returned HTTP {response.status}")
    except urllib.error.URLError as exc:
        raise OSError(str(exc)) from exc


def _alert_evidence(
    request: AlertRequest,
    status: OperationsStatus,
    rationale: str,
    findings: tuple[str, ...] = (),
) -> AlertEvidence:
    destination = (
        "https://redacted"
        if request.transport is AlertTransport.WEBHOOK
        else Path(request.destination).name
    )
    return AlertEvidence(
        alert_id=request.alert_id,
        status=status,
        transport=request.transport,
        destination_redacted=destination,
        rationale=rationale,
        findings=findings,
    )
