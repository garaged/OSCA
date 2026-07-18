# M1.5–M1.6 recovery skeleton evidence

- **Status:** Draft — final source revision and CI run pending
- **Branch:** `agent/m1-recovery-skeleton`
- **Requirements:** REQ-0010, REQ-0013, REQ-0017, REQ-0018, REQ-0020
- **Decisions:** ADR-0009, ADR-0015, ADR-0016
- **Schema revisions:** `m1_0005`, `m1_0006`
- **OpenSpec change:** `m1-recovery-skeleton`
- **Validated:** 2026-07-18

## Delivered behavior

- Catalog-owned typed recovery metadata and Recovery-owned durable operation state.
- Consistent SQLite snapshot and deterministic allowlisted package construction.
- age v1 X25519 process boundary with shell-free invocation, timeout, cleanup, and safe errors.
- Non-mutating verification, explicit preview, package-bound plan, and new-location-only restore.
- Five post-restore checks and active-state invariance.
- Trusted capabilities, vault identity resolution, correlated telemetry, audit, and CLI commands.

## Local focused gates

| Gate | Result |
|---|---|
| Recovery contracts, package, age, service, Catalog, and migration tests | Pass |
| Focused recovery application set | Pass — 20 tests |
| Boundary, telemetry, CLI, persistence, and migration set | Pass — 9 tests |
| Strict mypy for changed slices | Pass |
| Ruff for changed slices | Pass |
| Strict OpenSpec validation | Pass — 2 items, 0 failures |

## Pending retained evidence

- Full locked Python 3.13 pytest, Ruff, and strict mypy CI results.
- Reference age executable interoperability.
- Final source checkpoint and workflow run identity.
- Secret scan and documentation-link validation.

## Residual risks and limitations

Identity loss is unrecoverable. The external age executable is a runtime prerequisite and
substitution boundary. Failed isolated output may require manual removal. Activation, remote
transport, automated retention, and full disaster recovery remain deferred beyond M1.
