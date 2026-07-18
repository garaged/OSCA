# M1 Exit Review Record

- **Milestone:** M1 — Secure Walking Skeleton
- **Review status:** Technically ready; authority acceptance pending
- **Decision authorities:** Product, architecture, security, and quality authorities
- **Baseline under review:** `c16119dbaf19004a92128d9db83f81846d4fd062`
- **Requirements:** REQ-0001–REQ-0020
- **Specification:** [M1 secure walking skeleton](../../specifications/m1-secure-walking-skeleton.md)
- **Risk class:** Governed high-risk foundation change
- **Review date:** 2026-07-18

This record consolidates evidence for the M1 acceptance decision. It does not replace the requirements, specification, ADRs, contract catalog, or slice evidence. “Proposed” does not grant acceptance.

## Acceptance matrix

| Criterion | Result | Primary evidence | Limitation or disposition |
|---|---|---|---|
| M1-AC-001 | Pass | [M1.1](../../../evidence/m1/m1-1-readiness-foundation.md), [M1.7](../../../evidence/m1/m1-7-documentation-operational-evidence.md) | Locked CPython 3.13 reference environment |
| M1-AC-002 | Pass | [M1.4](../../../evidence/m1/m1-4-durable-diagnostic-jobs.md) | Structural negative fixtures remain mandatory |
| M1-AC-003 | Pass | [M1.1](../../../evidence/m1/m1-1-readiness-foundation.md), [M1.4](../../../evidence/m1/m1-4-durable-diagnostic-jobs.md) | Presentation differs; semantics are shared |
| M1-AC-004 | Pass | [M1.1](../../../evidence/m1/m1-1-readiness-foundation.md) | IPv4 loopback is the reference listener |
| M1-AC-005 | Pass | [M1.1](../../../evidence/m1/m1-1-readiness-foundation.md) | Personal-server production certification is out of scope |
| M1-AC-006 | Pass | [M1.2–M1.3](../../../evidence/m1/m1-2-3-persistence-security-telemetry.md), [M1.5–M1.6](../../../evidence/m1/m1-5-6-recovery-skeleton.md) | CI secret scan supplements canary assertions |
| M1-AC-007 | Pass | [M1.2–M1.3](../../../evidence/m1/m1-2-3-persistence-security-telemetry.md) | Supported-OS claims require target-platform runs |
| M1-AC-008 | Pass | [M1.4](../../../evidence/m1/m1-4-durable-diagnostic-jobs.md) | Actor-scoped idempotency |
| M1-AC-009 | Pass | [M1.4](../../../evidence/m1/m1-4-durable-diagnostic-jobs.md) | Single-node explicit recovery policy |
| M1-AC-010 | Pass | [M1.4](../../../evidence/m1/m1-4-durable-diagnostic-jobs.md) | Versioned checkpoint compatibility |
| M1-AC-011 | Pass | [M1.1](../../../evidence/m1/m1-1-readiness-foundation.md) | Availability does not imply analytical correctness |
| M1-AC-012 | Pass | [M1.2–M1.3](../../../evidence/m1/m1-2-3-persistence-security-telemetry.md), [M1.4](../../../evidence/m1/m1-4-durable-diagnostic-jobs.md) | External exporters remain optional |
| M1-AC-013 | Pass | [M1.5–M1.6](../../../evidence/m1/m1-5-6-recovery-skeleton.md) | Production packages require external age |
| M1-AC-014 | Pass | [M1.5–M1.6](../../../evidence/m1/m1-5-6-recovery-skeleton.md) | Malicious-input limits remain governed |
| M1-AC-015 | Pass | [M1.5–M1.6](../../../evidence/m1/m1-5-6-recovery-skeleton.md) | Activation is deferred |
| M1-AC-016 | Pass | [M1.2–M1.3](../../../evidence/m1/m1-2-3-persistence-security-telemetry.md), [M1.5–M1.6](../../../evidence/m1/m1-5-6-recovery-skeleton.md) | Revisions `m1_0001`–`m1_0006` retained |
| M1-AC-017 | Pass | [M1.4](../../../evidence/m1/m1-4-durable-diagnostic-jobs.md), [M1.5–M1.6](../../../evidence/m1/m1-5-6-recovery-skeleton.md) | Major-version rejection is fail closed |
| M1-AC-018 | Pass | [M1.7](../../../evidence/m1/m1-7-documentation-operational-evidence.md) | Credential examples remain operator supplied |
| M1-AC-019 | Pass | `tests/integration/test_m1_performance_budgets.py` | Reference observations only; not production SLOs |
| M1-AC-020 | Pass | [Integrated exit evidence](../../../evidence/m1/m1-exit-evidence.md) and [traceability register](../../governance/traceability-register.md) | Authority acceptance remains distinct from technical traceability |

## M1-AC-019 observation policy

The exit gate measures the six specification targets in the locked reference environment:

- process import/startup under five seconds;
- readiness processing p95 under one second over 100 samples;
- durable submission acknowledgement under one second;
- submitted state immediately observable within the five-second budget;
- named-phase progress within two seconds;
- cancellation acknowledgement within two seconds.

The test records pass/fail against these budgets. Environment timing is a bounded development/CI observation, not a production availability or latency guarantee. DD-010 remains the authority for future numeric production budgets.

## Contract and compatibility disposition

All implemented M1 public families remain at exact revision 1.0.0. Their deterministic schemas, round trips, semantic fixtures, unknown-major rejection, migrations, and recovery compatibility behavior are exercised by the retained suites. On final green validation, the contract catalog may mark all M1 families **Supported**. No deprecation, breaking revision, or compatibility exception is active.

SQLite revisions `m1_0001` through `m1_0006` remain retained. Backup manifests declare source build/schema compatibility, incompatible packages fail before restore writes, and M1 does not activate restored state.

## Specification open-question disposition

| Question | M1 disposition | Owner and revisit trigger |
|---|---|---|
| Dual-stack loopback: one listener or platform-dependent listeners | M1 supports the validated IPv4 loopback reference path. Additional IPv6 listener realization is platform-dependent guidance, not a second hidden requirement. | Architecture and security authorities; revisit before claiming a supported platform requires dual-stack binding. |
| Supported operating systems for credential-store conformance | M1 makes no named supported-OS claim. The keyring port and deterministic adapters are evidenced; real credential-store support requires target-platform conformance. | Security and product authorities; revisit before publishing the first supported-platform matrix. |

These dispositions narrow claims without changing accepted product behavior.

## Residual risks and deferred work

| Item | Disposition |
|---|---|
| Platform credential-store variation | Residual; target-platform conformance required before support claim |
| Dual-stack listener variation | Residual; IPv4 loopback is the reference path |
| Personal-server hardening and multi-user identity | Deferred beyond M1 |
| External telemetry exporters | Deferred; built-in health remains independent |
| SQLite sustained concurrency | Residual with WAL/short-transaction controls; revisit on measured contention |
| Embedded executor supervision and distributed work | Deferred beyond M1 |
| Recovery identity loss | Accepted residual operational risk; loss is unrecoverable |
| Restore activation, remote transport, retention automation, full DR | Deferred beyond M1 |
| Audit tamper evidence and retention hardening | Deferred unless a later requirement selects it |
| MkDocs Material and OCI profile recommendations | Not adopted as M1 normative obligations; revisit when documentation-site or personal-server packaging scope is selected |

No active architecture exception is recorded. No deferred item is silently implemented as an architectural default.

## Authority decision

Technical readiness requires a final green source revision, complete integrated evidence, synchronized indexes, and an archived OpenSpec change. After those conditions are met, product, architecture, security, and quality authorities must record **Accepted** or return blocking findings. Until then, M1 remains implementation complete but not milestone accepted.
