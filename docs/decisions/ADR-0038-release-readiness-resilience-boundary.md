# ADR-0038: Release Readiness and Operational Resilience Boundary

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Product authority, architecture authority, security authority, quality authority
- **Technical Story:** M12 release readiness and operational resilience

## Context

M12 closes the initial roadmap by making OSCA's operational readiness governable. The PRD requires secure operation, backup and disaster recovery, health, alerts, durable workflows, and deterministic risk policy behavior. Earlier milestones created skeletons and domain-specific controls, but a release-readiness layer needs shared evidence contracts before real off-device delivery, scheduler execution, personal-server hardening, or live trading can be safely implemented.

## Decision

M12 establishes operations evidence contracts before runtime integrations. Backup package manifests must declare encrypted profile, recovery point identity, integrity digest, recovery classes, off-device intent, exclusions, and secret-reference-only behavior. Restore verification must happen against an isolated target and fail closed when integrity, compatibility, journal reconciliation, or isolation evidence is missing.

Disaster-recovery exercises, health findings, alert policies, workflow runs, and risk-policy decisions are retained as typed metadata. Financially meaningful missed workflow runs require approval. Risk decisions reject breached strict controls and require explicit authority for modified outcomes.

SQLite persistence stores metadata only and supports component, workflow, and policy scoped queries.

## Consequences

- Release-readiness behavior has stable evidence contracts before production integrations.
- Backup and restore safety is inspectable without executing active restores.
- Alert policy metadata can be validated while external delivery remains deferred.
- Durable workflow missed-run behavior cannot silently replay financially meaningful work.
- Deterministic risk policy remains authoritative over ML, LLM, and strategy outputs.
- Real off-device transport, external delivery, scheduler execution, live execution, and provider production promotion remain deferred.
