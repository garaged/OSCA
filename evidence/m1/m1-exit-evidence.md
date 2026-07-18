# M1 integrated exit evidence

- **Status:** Accepted
- **Validated source checkpoint:** `9d3c06e0d06711a700fdfc3f278493b2ddef03f8`
- **Branch:** `agent/m1-exit-review`
- **GitHub Actions run:** `29653971594`
- **Requirements:** REQ-0001–REQ-0020
- **Acceptance criteria:** M1-AC-001–M1-AC-020
- **Decisions:** ADR-0001–ADR-0016
- **Risk class:** Governed high-risk foundation
- **Validated:** 2026-07-18

## Integrated conclusion

The retained M1.1–M1.7 records and the [M1 exit review](../../docs/milestones/m1/exit-review.md) provide complete technical traceability from intent through requirements, architecture, specification, validation, documentation, and evidence. No failed criterion, active exception, incompatible contract revision, destructive migration, secret finding, or architectural drift is known.

Product, architecture, security, and quality authorities accepted this evidence package on 2026-07-18 against technical head `e109b7027af3f8ac9e8dbb31137a3382adafa352`.

## Final technical gates

GitHub Actions run `29653971594` passed against the validated source checkpoint:

- locked CPython 3.13 environment;
- Ruff;
- strict mypy;
- full pytest, including M1-AC-019 reference observations;
- contract, schema, migration, documentation-link, and architecture checks;
- OpenSpec doctor and strict validation;
- secret scan.

## M1-AC-019

The bounded gate verified:

| Observation | Budget | Result |
|---|---:|---|
| Process import/startup | < 5 s | Pass |
| Readiness processing p95, 100 samples | < 1 s | Pass |
| Durable submission acknowledgement | < 1 s | Pass |
| Submitted state visibility | < 5 s | Pass |
| Named-phase progress | < 2 s | Pass |
| Cancellation acknowledgement | < 2 s | Pass |

These are locked reference-environment observations, not production SLOs. Future numeric production budgets remain governed by DD-010.

## Compatibility and recovery

All M1 public contract families are at 1.0.0 with deterministic schemas and conformance coverage. Unknown major versions fail closed. Alembic revisions `m1_0001`–`m1_0006` are retained. Backup verification checks build/schema compatibility before restore writes, and restore remains isolated and inactive.

## Security and exceptions

Loopback safety, personal-server prerequisite rejection, trusted authorization, named secret references, recursive redaction, malicious recovery input, audit separation, and secret scanning pass. No architecture exception is active. M1 does not claim public-internet certification or named operating-system credential-store support.

## Residual risks and deferred work

The exit review retains platform credential-store variation, dual-stack variation, SQLite contention triggers, recovery identity loss, and operator custody as residual risks. Multi-user identity, distributed execution, external workflow supervision, restore activation, remote backup transport, retention automation, full DR, MkDocs site generation, and OCI packaging are explicitly deferred and do not become implicit defaults.

## Integrity

The source checkpoint and immutable Actions run identify the validated technical material. Subsequent evidence/index/archive commits must pass the same PR gates. Final milestone status must name the authority decision and exact reviewed head.
