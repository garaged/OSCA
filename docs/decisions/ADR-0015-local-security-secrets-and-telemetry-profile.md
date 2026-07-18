# ADR-0015 — Local Security, Secrets, and Telemetry Profile

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Security authority and architecture authority
- **Scope:** M1 local-owner profile, personal-server configuration skeleton, secret adapter, and telemetry implementation
- **Related requirements:** REQ-0006 through REQ-0010, REQ-0014 through REQ-0016
- **Related product decisions:** D-031, D-032, D-035
- **Supersedes:** DD-012 for the M1 local profile and secret-vault adapter
- **Superseded by:** None

## Context

M1 must be frictionless and safe on a workstation while preventing accidental remote exposure, secret disclosure, or dependence on external observability infrastructure.

## Decision

The default local profile binds only to `127.0.0.1` and `::1`. Non-loopback binding requires explicit personal-server profile selection. That profile fails startup validation unless TLS identity/trust configuration and an authenticated application-session provider are present.

Ordinary secrets use an OS credential-store adapter through Python `keyring`, behind an OSCA-owned vault port. Tests use a non-production in-memory adapter. Secret values cannot appear in ordinary configuration, public contracts, telemetry, diagnostics, or backup content.

M1 emits structured JSON logs and uses OpenTelemetry APIs/SDK for traces and metrics. The built-in health capability remains independently usable without an external collector. Audit records are distinct from diagnostic telemetry and receive separate schema, access, integrity, and retention treatment.

Backup encryption format is not selected by this ADR. The recovery specification must choose an interoperable reviewed format; ad-hoc cryptographic containers are prohibited.

## Consequences

Native credential stores preserve platform security but require adapter conformance tests and documented platform behavior. Personal-server serving is configuration-complete but not advertised as production internet hardening in M1. Optional telemetry export cannot become required for local diagnosis.

## Fitness

- default configuration cannot listen beyond loopback;
- unsafe binding combinations fail before serving;
- invalid or missing TLS/session prerequisites fail closed;
- secret canaries never appear in logs, errors, schemas, manifests, backups, or bundles;
- vault adapter conformance covers store, resolve, rotate/reference update, delete, unavailable, and denied behavior;
- telemetry correlation spans interface request, application call, job, persistence, and audit event;
- built-in health works with exporters disabled.

## Revisit triggers

Multi-user identity, managed hosting, hardware-backed credentials, remote secret service, compliance profile, or external telemetry requirements.
