# ADR-0010: Unified Observability Architecture

- **Status:** Frozen
- **Tier:** Foundational
- **Date:** 2026-07-17

## Context

OSCA must support incident investigation, security review, workflow diagnosis, replay, recovery, extension governance, and architecture fitness through a coherent operational language rather than unrelated logs and metrics.

## Decision

Treat observability as a first-class architectural contract spanning every capability.

Significant operations emit standardized structured logs, metrics, traces, health information, and—where governance or security requires it—separate tamper-evident audit records.

The shared correlation model includes, where applicable:

- request identifier;
- correlation and causation identifiers;
- workflow identifier;
- actor or service identity;
- owning capability;
- contract family, compatibility version, and revision;
- extension identity and trust tier;
- execution, occurrence, and recording timestamps;
- replay, recovery, or degraded-mode markers.

Telemetry is emitted at architectural boundaries including public seams, commands, queries, event publication and consumption, workflow transitions, provider calls, extension execution, authorization decisions, and recovery operations.

Telemetry schemas and semantic definitions are versioned and governed. Sensitive data follows classification and redaction rules. Audit records remain distinct from operational telemetry. Health contracts are consistent across capabilities and must distinguish readiness, liveness, dependency health, degraded operation, and recovery state.

A feature is incomplete until it emits the telemetry required for operation, diagnostics, security, governance, and recovery. Architecture fitness and quality gates validate observability completeness.

## Consequences

Incident reconstruction and operational automation become consistent across capabilities and deployment models. Contributors must design telemetry with each feature, and tooling must validate schema compatibility, redaction, correlation, and health behavior.

## Rejected alternatives

- Independent, implementation-specific logging, metrics, and tracing.
- Using integration events as the primary observability mechanism.
