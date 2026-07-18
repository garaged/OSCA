# M1.5–M1.6 recovery skeleton evidence

- **Status:** Complete
- **Source checkpoint:** `4892e88ad8e1711e9bbbe51d296f3460eb9ea3ee`
- **Branch:** `agent/m1-recovery-skeleton`
- **GitHub Actions run:** `29652513765`
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

## Retained CI evidence

GitHub Actions run `29652513765` passed on the source checkpoint:

- locked CPython 3.13.14 environment;
- Ruff;
- strict mypy — 74 source files;
- pytest — 67 tests, including pinned age v1.3.1 bidirectional interoperability;
- migration, contract, architecture-boundary, and documentation-link checks;
- strict OpenSpec validation;
- secret scan.

The single pytest warning is the intentional duplicate-ZIP-entry malicious fixture and does not indicate product behavior.

## Residual risks and limitations

Identity loss is unrecoverable. The external age executable is a runtime prerequisite and
substitution boundary. Failed isolated output may require manual removal. Activation, remote
transport, automated retention, and full disaster recovery remain deferred beyond M1.
