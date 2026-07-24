# M1 protected backup and isolated restore

- **Status:** Implemented with retained CI evidence
- **Requirements:** REQ-0010, REQ-0013, REQ-0017, REQ-0018
- **Governing decisions:** ADR-0009, ADR-0015, ADR-0016
- **Contracts:** `osca.recovery.backup-manifest` 1.0.0 and `osca.recovery.restore-plan` 1.0.0

## Normative behavior

The [M1 recovery specification](../../../openspec/specs/m1-recovery-skeleton/spec.md) and
[M1 recovery decision record](../../../openspec/changes/archive/2026-07-18-m1-recovery-skeleton/README.md)
govern behavior. This page is operator guidance and does not redefine those sources.

Production output is an age v1 binary container encrypted to an X25519 recipient. Plaintext
packages are test fixtures only. Verification and preview do not write active state. Restore
creates a new destination and never activates or overwrites active state.

## Prerequisites

1. Install a compatible `age` executable. Set `OSCA_AGE_PATH` when it is not at
   `/usr/bin/age` or discoverable on `PATH`.
2. Generate and custody an X25519 identity independently of the protected data.
3. Store the private identity through the Security capability in the OS credential store under
   namespace `recovery`. CLI arguments use only its identity name.
4. Retain the public `age1...` recipient for backup creation.
5. Set `OSCA_DATABASE_PATH` and apply migrations through `m1_0006`.

Loss of every private recovery identity makes the package unrecoverable. Copying an identity into
the backup, configuration, command line, logs, or documentation is prohibited.

## Commands

```bash
osca backup-create /protected/osca-backup.age age1example
osca backup-verify /protected/osca-backup.age primary-age-identity
osca restore-preview /protected/osca-backup.age /isolated/osca-restore primary-age-identity
osca restore-isolated /protected/osca-backup.age /isolated/osca-restore primary-age-identity
```

The recipient above is a non-executable placeholder. Use the exact public recipient produced by
`age-keygen`.

## Package and validation behavior

The decrypted allowlist contains `manifest.json`, `state/osca.db`,
`configuration/snapshot.json`, and `exclusions.json`. Verification rejects authentication
failure, checksum mismatch, invalid manifest integrity, unknown or duplicate entries, unsafe
paths, non-regular entries, size-limit violations, and package changes during verification.

Post-restore checks cover SQLite integrity, exact schema compatibility, Catalog/reference
structure, audit structure, and a read-only readiness smoke query. Failed isolated output may
remain for diagnosis, but active state is not changed.

## Troubleshooting

| Code | Meaning | Safe response |
|---|---|---|
| `recovery.encryption.unavailable` | The configured age executable cannot run | Verify installation and `OSCA_AGE_PATH` |
| `recovery.recipient.invalid` | Recipient is unsupported | Use the public X25519 recipient |
| `recovery.identity.missing` | The vault reference cannot resolve | Restore the identity to the OS credential store |
| `recovery.decryption.failed` | Authentication failed | Verify identity custody and package provenance |
| `recovery.package.entries_invalid` | Archive allowlist failed | Treat the package as corrupt or malicious |
| `recovery.destination.exists` | Restore target is not new | Choose a new isolated destination |
| `recovery.restore.integrity_failed` | A post-restore check failed | Diagnose the isolated output; do not activate it |

## M1 limitations

Activation, in-place restore, remote storage, scheduling, automated retention, and market
payloads are out of scope. Production use depends on an external compatible age executable. The
accepted M1 identity profile is age v1 X25519; plugins and passphrases are not defaults.
