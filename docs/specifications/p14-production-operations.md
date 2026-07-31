# P14 Personal-Server Production Operations Specification

## Purpose

Provide explicit, evidence-retaining operations for a trusted single-user OSCA host.

## Phase

Production-capable version

## User-visible value

An operator can schedule governed commands, deliver configured alerts, create and restore off-source backups, and deploy hardened service templates.

## Requirements

- **REQ-0254:** OSCA must validate personal-server exposure and reject non-loopback binding unless TLS and authentication are enabled.
- **REQ-0255:** OSCA must execute only explicitly enabled scheduled commands with bounded timeout and retained run evidence.
- **REQ-0256:** OSCA must deliver alerts only through explicitly enabled file or HTTPS-webhook transports and must redact webhook destinations from evidence.
- **REQ-0257:** OSCA must create backups outside the source tree with a manifest, file count, and SHA-256 digest.
- **REQ-0258:** OSCA must restore archives through path-safe staging and require explicit overwrite permission for non-empty destinations.
- **REQ-0259:** OSCA must provide hardened single-user deployment templates without representing them as complete infrastructure automation.
- **REQ-0260:** P14 completion requires manual usage, traceability, OpenSpec, automated validation, and hosted Quality evidence.

## Implementation scope

- Frozen scheduler, alert, backup, restore, security, and evidence contracts.
- CLI-controlled operational execution with explicit enablement.
- File and HTTPS-webhook alerts.
- tar.gz backup and active restore execution.
- systemd service/timer templates with common hardening directives.

## Explicit non-scope

- Multi-tenant SaaS, public anonymous access, managed infrastructure provisioning, remote arbitrary command control, broker/exchange connections, autonomous trading, or real-money execution.

## Acceptance criteria

- Disabled operations return structured `policy_blocked` evidence.
- Security validation fails closed for unsafe exposure.
- Backup/restore tests cover source separation, archive safety, and overwrite behavior.
- Scheduler and alert tests cover successful and blocked behavior.
- Documentation distinguishes implementation from operator-owned infrastructure controls.

## Dependencies

P10-P13 and M12 operations/recovery contracts.

## Risks and decisions

A trusted single-user host remains the supported deployment model. Operators own host patching, firewalling, TLS certificates, identities, off-device storage access, and post-restore application validation.
