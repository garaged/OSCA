# ADR-0005: Risk-Tiered Quality Gate Enforcement

- **Status:** Frozen
- **Date:** 2026-07-17
- **Decision owners:** Architecture authority and engineering governance
- **Related:** ADR-0001, ADR-0003, ADR-0004; `docs/quality/verification-strategy.md`

## Context

OSCA requires strong evidence for reproducibility, financial and risk correctness, security, migrations, public contracts, extensions, and recovery. A universal maximum test suite would be slow and brittle, while advisory checks would allow architecture and compatibility debt to accumulate.

## Decision

OSCA will enforce **risk-tiered mandatory quality gates**.

Every change must pass a baseline gate set. Additional mandatory gates are selected from the change's affected capabilities, contract families, data ownership, security boundaries, recovery impact, and operational risk.

### Baseline gates

Every change must provide, where applicable:

- a successful build;
- formatting and static-analysis compliance;
- module dependency and cycle validation;
- relevant unit and component tests;
- requirement and specification traceability;
- documentation and link validation;
- secret scanning and critical dependency checks.

### Elevated gates

Public-contract changes require compatibility, migration, replay, catalog, and manifest evidence.

Persistence changes require historical-state migration, interrupted-migration recovery, integrity, reconciliation, and backup/restore evidence.

Financial, risk, accounting, identity, and authorization changes require invariant, property, deterministic reference, denial-path, and edge-case tests.

Security-sensitive changes require a threat-model delta, authorization evidence, audit and secret controls, and designated security review.

Performance-sensitive changes require baseline comparison, resource-budget analysis, and approval for material regressions.

Recovery-sensitive changes require restore, degraded-mode, failover or restart, and runbook evidence.

### Classification and authority

- Risk classification is machine-assisted and reviewable.
- Authors cannot unilaterally downgrade high-risk changes.
- Capability owners may raise the required tier.
- Protected financial, security, migration, and public-contract changes require designated review authority.

### Exceptions

A mandatory gate may be waived only by an explicit, expiring exception containing:

- the affected rule and evidence;
- the reason and risk;
- owner and approver;
- compensating controls;
- remediation deadline;
- automated visibility and expiry enforcement.

Expired unresolved exceptions block release.

### Execution policy

- Fast deterministic gates run first.
- Expensive suites run when impact requires them and in scheduled full-suite verification.
- Flaky tests remain visible, assigned, and time-bounded; they cannot silently become optional.
- Release gates are stricter than ordinary merge gates.
- Required gates and outcomes are retained as milestone and release evidence.

## Consequences

### Positive

- Verification effort is proportional to actual risk.
- High-impact changes receive strong, explicit evidence.
- Feedback remains fast for low-risk work.
- Governance, traceability, and exceptions become auditable.

### Negative

- Change classification and CI orchestration become more sophisticated.
- Gate ownership and exception management require active maintenance.
- Incorrect classification can omit evidence unless reviews and fitness checks detect it.

## Fitness obligations

Future implementation must prove that:

- protected path changes cannot bypass elevated gates;
- required gate selection is visible before merge;
- exceptions expire automatically;
- full-suite scheduled results are retained;
- release evidence includes unresolved risks and exceptions.
