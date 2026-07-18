## Why

M1 still lacks the protected recovery path required to begin later product implementation with credible state protection. M1.5 is partially complete because diagnostic result metadata exists, but backup metadata does not; M1.6 remains unimplemented. This change completes that bounded vertical slice under REQ-0010, REQ-0013, REQ-0017, REQ-0018, REQ-0020, the accepted M1 specification, and ADR-0016.

## What Changes

- Complete Catalog-owned typed backup and restore metadata.
- Create consistent minimal SQLite snapshots and deterministic manifests with checksums and exclusions.
- Encrypt production packages as `age/v1+x25519` through a bounded shell-free adapter.
- Verify/decrypt without active-state mutation.
- Produce explicit restore previews and conflict reports.
- Restore only into a new isolated location and execute post-restore validation.
- Emit correlated telemetry and distinct audit records.
- Add recovery, migration, security-negative, compatibility, documentation, and retained evidence.

## Capabilities

### New Capabilities

- `m1-recovery-skeleton`: Protected backup creation, verification, preview, and isolated restore for M1 state.

### Modified Capabilities

None. The accepted M1 specification remains authoritative; this change narrows its M1.5/M1.6 implementation slice.

## Impact

- **Owning capability:** Recovery owns manifests, package orchestration, verification, restore plans, and restore records.
- **Affected contracts:** `osca.recovery.backup-manifest` 1.0.0, `osca.recovery.restore-plan` 1.0.0, and `osca.error.envelope` 1.0.0.
- **Supporting capabilities:** Catalog owns retained metadata; Security resolves private identity references; Operations owns telemetry, findings, and audit.
- **Governing architecture:** ADR-0003, ADR-0004, ADR-0005, ADR-0006, ADR-0009, ADR-0010, ADR-0012, ADR-0014, ADR-0015, ADR-0016.
- **Risk class:** Governed high-risk recovery and security change.
- **Non-goals:** restored-state activation, full disaster-recovery automation, remote backup transport, retention scheduling, distributed coordination, and market payload backup.
