# M1 Evidence Plan

- **Status:** Accepted
- **Governing role:** Quality authority
- **Architecture and security approval:** Required
- **Governing specification:** [M1 secure walking skeleton](../../specifications/m1-secure-walking-skeleton.md)
- **Last reviewed:** 2026-07-18

## Risk classification

M1 is a **governed high-risk foundation change** under ADR-0005 because it establishes public contracts, security defaults, persistent state, durable execution, migrations, audit behavior, and recovery formats.

## Required gates

### Fast pull-request gates

- locked-environment verification;
- formatting and Ruff;
- mypy strict;
- unit and property tests;
- module-boundary/import/cycle checks;
- YAML/JSON/schema/link validation;
- secret scanning;
- deterministic OpenAPI/schema generation;
- documentation example tests.

### Component and contract gates

- configuration and readiness component suites;
- API/CLI semantic contract fixtures;
- vault adapter conformance;
- job lifecycle/idempotency/lease/cancellation tests;
- repository ownership tests;
- health aggregation properties;
- telemetry and audit assertions;
- compatibility fixtures.

### Security and recovery gates

- unsafe-bind and remote-profile negative tests;
- secret canary scan;
- malicious input/archive/path tests;
- migration and interrupted-migration tests;
- consistent backup and integrity verification;
- corrupt/incompatible backup rejection;
- isolated restore with active-state immutability;
- post-restore readiness and reconciliation.

### End-to-end and documentation gates

- local startup and three-interface readiness;
- diagnostic job submit/progress/restart/resume/result;
- backup/verify/preview/isolated-restore;
- version-matched setup and task examples;
- basic accessibility and semantic HTML inspection.

## Evidence retention

M1 evidence is recorded under `evidence/m1/` with source SHA, environment/tool versions, lock digest, schema revisions, fixture digests, results, limitations, exceptions, and integrity digest. Generated bulk output may remain in CI retention while the repository record links its immutable run identity.

Retained slice records:

- [M1.1 readiness foundation](../../../evidence/m1/m1-1-readiness-foundation.md)
- [M1.2–M1.3 persistence, security, and telemetry](../../../evidence/m1/m1-2-3-persistence-security-telemetry.md)
- [M1.4 durable diagnostic jobs](../../../evidence/m1/m1-4-durable-diagnostic-jobs.md)
- [M1.5–M1.6 recovery skeleton](../../../evidence/m1/m1-5-6-recovery-skeleton.md)
- [M1.7 documentation and operational evidence](../../../evidence/m1/m1-7-documentation-operational-evidence.md)

## Merge policy

No implementation slice merges with a failing required gate. A temporary exception must use `EXC-NNNN`, expire, retain blocking visibility, and receive the governing authority's approval.
