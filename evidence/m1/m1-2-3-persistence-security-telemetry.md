# M1.2–M1.3 Persistence, Security, and Telemetry Evidence

- **Status:** Complete
- **Source branch:** `agent/m1-secure-walking-skeleton`
- **Requirements:** REQ-0006–REQ-0010, REQ-0013–REQ-0016, REQ-0020 (incremental realization)
- **Specification:** [M1 secure walking skeleton](../../docs/specifications/m1-secure-walking-skeleton.md)
- **ADRs:** ADR-0003, ADR-0005, ADR-0009, ADR-0010, ADR-0012, ADR-0015
- **Executed:** 2026-07-18
- **Risk class:** Governed high-risk foundation

## Evidence

| Area | Evidence | Result |
|---|---|---|
| Locked environment | Python 3.13.14 and committed `uv.lock` | Pass |
| Full suite | pytest | 21 passed |
| Static quality | Ruff across source, tests, and migrations | Pass |
| Type safety | mypy strict | Pass across 37 source files |
| SQLite policy | WAL, foreign keys, 5000 ms busy timeout | Pass |
| Integrity | SQLite `integrity_check` | Pass |
| Ownership | Configuration and Operations use separate declarative metadata/tables/repositories | Pass |
| Configuration round trip | Immutable versioned snapshot | Pass |
| Duplicate configuration revision | Primary-key rejection | Pass |
| Migration | `m1_0001` plus `m1_0002` upgrade and full downgrade | Pass |
| Vault conformance | In-memory and injected keyring adapters | Pass |
| Secret-safe probe | Public result contains reference/status only | Pass |
| Redaction | Nested secret/token fields removed from structured JSON logs | Pass |
| Telemetry | Local OpenTelemetry providers require no collector | Pass |
| Audit separation | Typed audit record and Operations-owned persistence | Pass |

## Implemented controls

- capability-owned repository ports and adapters;
- SQLite WAL, integrity, timeout, and transaction controls;
- initial retained migration history;
- OS credential-store adapter through `keyring`;
- deterministic non-production vault adapter;
- structured vault failure classification;
- JSON logging with recursive sensitive-field redaction;
- local OpenTelemetry tracer and meter providers;
- distinct, payload-constrained audit records and storage.

## Limitations

- Real platform credential-store behavior requires supported-OS integration runs.
- Audit tamper-evidence, retention, and authorized query behavior remain for later M1 hardening.
- External telemetry exporters are intentionally absent; built-in health must remain independent.
- Durable workflow tables and behavior begin in M1.4.

## Conclusion

M1.2 and the foundational M1.3 controls are complete with no active exception. The branch may proceed to the durable diagnostic-job increment.
